package com.iitb.faas.RegistryService;

import java.io.IOException;
import java.sql.Timestamp;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.springframework.beans.BeansException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.ApplicationContext;
import org.springframework.context.ApplicationContextAware;
import org.springframework.data.redis.connection.jedis.JedisConnectionFactory;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.exceptions.JedisException;

@Component
public class TriggerUtil implements ApplicationContextAware {

	private static ApplicationContext context;
	private static String downlineUrl;

	private static final int POLDURATION_MIN = 10;
	private static final int POLINTERVAL_SEC = 10;

	private static AtomicInteger sharedTriggerCount = new AtomicInteger(0);
	private static ThreadLocal<Integer> threadLocalCount = ThreadLocal.withInitial(() -> 0);

	@Override
	public void setApplicationContext(ApplicationContext applicationContext) throws BeansException {
		context = applicationContext;
	}

	@Value("${downline_url}")
	public void setDownlineUrl(String downlineUrl) {
		TriggerUtil.downlineUrl = downlineUrl;
	}

	public static void handleTrigger(FnRegistry savedFnRegistry, String message) {

		/*
		 * Setup the counter variables to handle multiple triggers
		 */
		setLocalCounter();
		/*
		 * Getting Spring beans from context to use further
		 */
		if (context == null) {
			throw new IllegalStateException("ApplicationContext is not set.");
		}
		FnRegistryRepository fnRegistryRepository = context.getBean(FnRegistryRepository.class);
		RestTemplate restTemplate = context.getBean(RestTemplate.class);
		JedisConnectionFactory jedisConnectionFactory = context.getBean(JedisConnectionFactory.class);

		/*
		 * Creates Job Queue with current Function name and Bucket ID. Pushes IDs passed
		 * by the Publisher into the newly created Queue
		 */
		String fnNm_buckId_queue = savedFnRegistry.getFnName() + "_" + savedFnRegistry.getBucketId() + "_" + "queue";
		createIDQueue(jedisConnectionFactory, message, fnNm_buckId_queue);

		/*
		 * Update Function status and Trigger time into Function registry as PROCESSING
		 */
		FnRegistry fnRegistry = fnRegistryRepository.findById(savedFnRegistry.getFnId()).orElse(null);
		if (fnRegistry == null) {
			throw new RuntimeException("Function Registry not found for ID " + savedFnRegistry.getFnId());
		}

		fnRegistry.setTriggerTime(Timestamp.from(Instant.now()));
		fnRegistry.setStatus(Status.PROCESSING);
		fnRegistry = fnRegistryRepository.save(fnRegistry);

		/*
		 * Triggering Downline service to process the Function
		 */
		System.out.println("\n--- Running downline Trigger handler  ---\n");

		String url_dispatch = downlineUrl + "/api/v1/dispatch";
		ResponseEntity<String> response = downline_post(fnRegistry, url_dispatch, restTemplate);

		if (response.getStatusCode() != HttpStatus.CREATED) {
			fnRegistry.setStatus(Status.FAILED);
			throw new RuntimeException(
					"Failed to trigger DOWNLINE. Unexpected status code: " + response.getStatusCode().value());
		}

		/*
		 * The triggPoll Downline status endpoint to check for the completion status of
		 * the Function
		 */
		String url_status = downlineUrl + "/api/v1/status/" + fnRegistry.getFnName();

		Map<String, String> finalPollResp = pollStatus(restTemplate, url_status);

		/*
		 * Save final poll Status to Function Registry and removing the queue from Redis
		 * server
		 */
		if (sharedTriggerCount.get() == threadLocalCount.get()) {

			String finalStatus = finalPollResp.get("status");
			Timestamp finishTimestamp = finalPollResp.get("finishTime") != null
					? Timestamp.from(OffsetDateTime.parse(finalPollResp.get("finishTime")).toInstant())
					: null;

			fnRegistry.setStatus(Status.valueOf(finalStatus));
			fnRegistry.setFinishTime(finishTimestamp);
			
			if(fnRegistryRepository.findById(fnRegistry.getFnId()) != null){
				fnRegistryRepository.save(fnRegistry);
			}

			removeIDQueue(jedisConnectionFactory, fnNm_buckId_queue);

			System.out.println("Final status after polling: " + finalStatus);
		} else {
			System.out.println("Obsolute polling thread exiting..");
		}

	}

	private static ResponseEntity<String> downline_post(FnRegistry downlineRequest, String url, RestTemplate template) {

		HttpHeaders headers = new HttpHeaders();
		headers.setContentType(MediaType.APPLICATION_JSON);

		HttpEntity<FnRegistry> requestEntity = new HttpEntity<>(downlineRequest, headers);

		ResponseEntity<String> response = template.postForEntity(url, requestEntity, String.class);

		return response;
	}

	private static Map<String, String> pollStatus(RestTemplate restTemplate, String url) {

		LocalDateTime endTime = LocalDateTime.now().plusMinutes(POLDURATION_MIN);

		String status = Status.PROCESSING.name();
		Map<String, String> resp = new HashMap<String, String>();
		resp.put("status", status);

		while ((!status.equals(Status.FAILED.name())) && (!status.equals(Status.SUCCESS.name()))
				&& (sharedTriggerCount.get() == threadLocalCount.get())) {

			try {
				if (!LocalDateTime.now().isBefore(endTime)) {
					throw new RuntimeException("Time out polling");
				}
				TimeUnit.SECONDS.sleep(POLINTERVAL_SEC);

				// Make request and get status
				resp = getStatus(restTemplate, url);

				// Logging
				status = resp.get("status");
				System.out.println("Current poll status: " + status);

			} catch (Exception e) {
				Thread.currentThread().interrupt();
				e.printStackTrace();

				resp.put("status", Status.FAILED.toString());
				return resp;
			}
		}
		return resp;
	}

	private static Map<String, String> getStatus(RestTemplate restTemplate, String url) {

		ResponseEntity<String> responseEntity = restTemplate.getForEntity(url, String.class);

		HttpStatusCode statusCode = responseEntity.getStatusCode();
		String responseBody = responseEntity.getBody();

		Map<String, String> statusResp = parseStatusResp(responseBody);

		if (statusCode != HttpStatus.OK) {
			Thread.currentThread().interrupt();
			System.err.println("Response status code: " + statusCode);

			statusResp.put("status", Status.FAILED.toString());
			return statusResp;
		}

		return statusResp;
	}

	private static Map<String, String> parseStatusResp(String responseBody) {
		ObjectMapper objectMapper = new ObjectMapper();
		try {

			return objectMapper.readValue(responseBody, new TypeReference<Map<String, String>>() {
			});
		} catch (IOException e) {

			e.printStackTrace();
			return Collections.emptyMap();
		}
	}

	private static String[] imageIDExtractor(String msg) {

		Pattern pattern = Pattern.compile("\\[(.*?)\\]");
		Matcher matcher = pattern.matcher(msg);
		String entries = "";
		if (matcher.find()) {
			entries = matcher.group(1);
		}
		String[] ids = entries.split(",\\s*");

		return ids;
	}

	private static void createIDQueue(JedisConnectionFactory jedisConnectionFactory, String message, String queue) {

		String[] imgIDs = imageIDExtractor(message);

		try (Jedis jedis = (Jedis) jedisConnectionFactory.getConnection().getNativeConnection()) {

			for (String id : imgIDs) {
				String trimmedId = id.trim().replaceAll("[\\[\\]]", "");

				jedis.lpush(queue, trimmedId);
			}

			System.out.println("Entries pushed successfully to Redis queue: " + queue);
		} catch (JedisException e) {
			System.err.println("Redis operation failed: " + e.getMessage());
		}
	}

	private static void removeIDQueue(JedisConnectionFactory jedisConnectionFactory, String queue) {

		try (Jedis jedis = (Jedis) jedisConnectionFactory.getConnection().getNativeConnection()) {

			jedis.del(queue);

			System.out.println("Deleted Redis queue: " + queue);
		} catch (JedisException e) {
			System.err.println("Redis operation failed: " + e.getMessage());
		}
	}

	private static synchronized void setLocalCounter() {
		threadLocalCount.set(sharedTriggerCount.incrementAndGet());
	}

}
