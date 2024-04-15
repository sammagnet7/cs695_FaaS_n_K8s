package com.iitb.faas.RegistryService;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class FnRegistryService {

	private final FnRegistryRepository fnRegistryRepository;

	private final RedisSubscriber redisSubscriber;

	@Autowired
	public FnRegistryService(FnRegistryRepository fnRegistryRepository, RedisSubscriber jedisSubscriber) {
		this.fnRegistryRepository = fnRegistryRepository;
		this.redisSubscriber = jedisSubscriber;
	}

	public void registerFunction(RegisterRequest registerRequest) {

		FnRegistry fnRegistry = new FnRegistry();
		setProperties(registerRequest, fnRegistry);

		FnRegistry savedFnRegistry = fnRegistryRepository.save(fnRegistry);
		int savedFnId = savedFnRegistry.getFnId();


		String channel_name = registerRequest.getBucketId() + "_" + registerRequest.getEventType() + "_" + "channel";

		Thread subscriptionThread = new Thread(() -> redisSubscriber.subscribeToChannel( channel_name,savedFnId ) );
		subscriptionThread.start();

	}

	public void deregisterFunction(int fnId) {

		FnRegistry fnRegistry = fnRegistryRepository.getById(fnId);

		String channel_name = fnRegistry.getBucketId() + "_" + fnRegistry.getEventType() + "_" + "channel";

		redisSubscriber.unsubscribeFromChannel(channel_name, fnId);

		fnRegistryRepository.deleteById(fnId);

	}

	public void setProperties(RegisterRequest registerRequest, FnRegistry fnRegistry) {

		fnRegistry.setFnName(registerRequest.getFnName());
		fnRegistry.setRuntime(registerRequest.getRuntime());
		fnRegistry.setSourceCode(registerRequest.getSourceCode());
		fnRegistry.setRequirements(registerRequest.getRequirements());
		fnRegistry.setEntryFn(registerRequest.getEntryFn());
		fnRegistry.setTriggerType(registerRequest.getTriggerType().toString());
		fnRegistry.setEventType(registerRequest.getEventType().toString());
		fnRegistry.setBucketId(registerRequest.getBucketId());
	}

}
