package com.iitb.faas.RegistryService;

import java.io.IOException;
import java.sql.Timestamp;
import java.time.Duration;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;

import org.springframework.beans.BeansException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.ApplicationContext;
import org.springframework.context.ApplicationContextAware;
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

@Component
public class TriggerUtil implements ApplicationContextAware {

	private static ApplicationContext context;

	private static String downlineUrl;

	private static final int POLDURATION_MIN = 5;
	private static final int POLINTERVAL_SEC = 10;

	@Override
	public void setApplicationContext(ApplicationContext applicationContext) throws BeansException {
		context = applicationContext;
	}

	@Value("${downline_url}")
	public void setDownlineUrl(String downlineUrl) {
		TriggerUtil.downlineUrl = downlineUrl;
	}

	public static void handleTrigger(int fn_id) {

		/*
		 * Getting Spring beans from context to use further
		 */
		if (context == null) {
			throw new IllegalStateException("ApplicationContext is not set.");
		}
		FnRegistryRepository fnRegistryRepository = context.getBean(FnRegistryRepository.class);
		RestTemplate restTemplate = context.getBean(RestTemplate.class);

		/*
		 * Update Function status and Trigger time into Function registry as PROCESSING
		 */
		FnRegistry fnRegistry = fnRegistryRepository.findById(fn_id).orElse(null);
		if (fnRegistry == null) {
			throw new RuntimeException("Function Registry not found for ID" + fn_id);
		}

		fnRegistry.setTriggerTime(Timestamp.from(Instant.now()));
		fnRegistry.setStatus(Status.PROCESSING);
		fnRegistry = fnRegistryRepository.save(fnRegistry);

		/*
		 * Triggering Downline service to process the Function
		 */
		System.out.println("\n--- Running downline Trigger handler ---\n");

		String url_dispatch = downlineUrl + "/api/v1/dispatch";
		ResponseEntity<String> response = downline_post(fnRegistry, url_dispatch, restTemplate);

		if (response.getStatusCode() != HttpStatus.CREATED) {
			fnRegistry.setStatus(Status.FAILED);
			throw new RuntimeException(
					"Failed to trigger DOWNLINE. Unexpected status code: " + response.getStatusCode().value());
		}

		/*
		 * Poll Downline status endpoint to check for the completion status of the Function
		 */
		String url_status = downlineUrl + "/api/v1/status/" + fnRegistry.getFnName();

		Map<String, String> finalPollResp = pollStatus(restTemplate, url_status);
		
		String finalStatus = finalPollResp.get("status");
		Timestamp finishTimestamp = Timestamp.from(OffsetDateTime.parse(finalPollResp.get("finishTime")).toInstant());

		/*
		 * Save final Status to Function Registry
		 */
		fnRegistry.setStatus(Status.valueOf(finalStatus));
		fnRegistry.setFinishTime(finishTimestamp);

		fnRegistry = fnRegistryRepository.save(fnRegistry);

		System.out.println("Final status after polling: " + finalStatus);
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
		String status = Status.CREATED.name();

		Map<String, String> resp = new HashMap<String, String>();
		while (!status.equals(Status.FAILED.name()) && !status.equals(Status.SUCCESS.name())
				&& LocalDateTime.now().isBefore(endTime)) {
			try {
				// Wait for 10 seconds before making the next request
				TimeUnit.SECONDS.sleep(POLINTERVAL_SEC);

				// Make request and get status
				resp = getStatus(restTemplate, url);

				// Logging
				status = resp.get("status");
				Duration remainingTime = Duration.between(LocalDateTime.now(), endTime);
				System.out.println("Remaining wait time: " + remainingTime.toSeconds() + " seconds");
				System.out.println("Current poll status: " + status);

			} catch (InterruptedException e) {
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

}
