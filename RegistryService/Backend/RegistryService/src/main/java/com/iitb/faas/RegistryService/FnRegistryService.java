package com.iitb.faas.RegistryService;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import jakarta.transaction.Transactional;

@Service
public class FnRegistryService {

	private final FnRegistryRepository fnRegistryRepository;
	private final RedisSubscriber redisSubscriber;
	private final RestTemplate restTemplate;
	private final String downlineUrl;

	@Autowired
	public FnRegistryService(FnRegistryRepository fnRegistryRepository, RedisSubscriber jedisSubscriber,
			RestTemplate restTemplate, @Value("${downline_url}") String downlineUrl) {
		this.fnRegistryRepository = fnRegistryRepository;
		this.redisSubscriber = jedisSubscriber;
		this.restTemplate = restTemplate;
		this.downlineUrl = downlineUrl;
	}

	@Transactional
	public void registerFunction(RegisterRequest registerRequest) {

		FnRegistry fnRegistry = new FnRegistry();
		setRepoProperties(registerRequest, fnRegistry);
		
		FnRegistry savedFnRegistry = fnRegistryRepository.save(fnRegistry);

		RegisterRequest_Downline downline_req = new RegisterRequest_Downline();
		setDownlineProperties(registerRequest, downline_req);
		String url_register = downlineUrl + "/api/v1/register";		
		
		ResponseEntity<String> response = downline_post(downline_req, url_register);
		
		if (response.getStatusCode() != HttpStatus.CREATED) {
			throw new RuntimeException("Failed to register function into DOWNLINE. Unexpected status code: "
					+ response.getStatusCode().value());
		}
		
		/*
		 * Subscribe on a channel creating a new thread
		 */
		redisSubscriber.subscribeToChannel(savedFnRegistry);

	}

	public void deregisterFunction(String fnName) {

		FnRegistry fnRegistry = fnRegistryRepository.findByFnName(fnName);

		String channel_name = fnRegistry.getBucketId() + "_" + fnRegistry.getEventType() + "_" + "channel";

		redisSubscriber.unsubscribeFromChannel(channel_name, fnRegistry.getFnId());

		fnRegistryRepository.deleteById(fnRegistry.getFnId());

	}

	public List<FnRegistry> getAllFunctions() {
		return fnRegistryRepository.findAll();
	}

	private void setRepoProperties(RegisterRequest registerRequest, FnRegistry fnRegistry) {

		fnRegistry.setFnName(registerRequest.getFnName());
		fnRegistry.setRuntime(registerRequest.getRuntime());
		fnRegistry.setSourceCode(registerRequest.getSourceCode());
		fnRegistry.setRequirements(registerRequest.getRequirements());
		fnRegistry.setEntryFn(registerRequest.getEntryFn());
		fnRegistry.setTriggerType(registerRequest.getTriggerType().toString());
		fnRegistry.setEventType(registerRequest.getEventType().toString());
		fnRegistry.setBucketId(registerRequest.getBucketName());

		fnRegistry.setStatus(Status.CREATED);
	}

	private void setDownlineProperties(RegisterRequest registerRequest, RegisterRequest_Downline downline) {

		downline.setFnName(registerRequest.getFnName());
		downline.setRuntime(registerRequest.getRuntime());
		downline.setSourceCode(registerRequest.getSourceCode());
		downline.setRequirements(registerRequest.getRequirements());

	}

	private ResponseEntity<String> downline_post(RegisterRequest_Downline downlineRequest, String url) {

		HttpHeaders headers = new HttpHeaders();
		headers.setContentType(MediaType.APPLICATION_JSON);

		HttpEntity<RegisterRequest_Downline> requestEntity = new HttpEntity<>(downlineRequest, headers);

		ResponseEntity<String> response = restTemplate.postForEntity(url, requestEntity, String.class);

		return response;
	}

}
