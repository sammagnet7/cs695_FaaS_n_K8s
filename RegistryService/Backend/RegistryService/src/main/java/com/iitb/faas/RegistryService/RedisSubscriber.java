package com.iitb.faas.RegistryService;

import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.connection.MessageListener;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.listener.ChannelTopic;
import org.springframework.data.redis.listener.RedisMessageListenerContainer;
import org.springframework.stereotype.Component;

@Component
public class RedisSubscriber {

	private final RedisMessageListenerContainer listenerContainer;
	private final Map<Integer, MessageListener> channelListeners = new HashMap<>();

	@Autowired
	public RedisSubscriber(RedisTemplate<String, Object> redisTemplate,
			RedisMessageListenerContainer listenerContainer) {
		this.listenerContainer = listenerContainer;

	}

	public void subscribeToChannel(FnRegistry savedFnRegistry) {

		String channel = savedFnRegistry.getBucketId() + "_" + savedFnRegistry.getEventType() + "_" + "channel";
		System.out.println("*** Subscribing to channel: " + channel + " ***");

		/*
		 * Creating a Redis listener which subscribe to the given channel
		 */
		MessageListener messageListener = (message, pattern) -> {

			System.out.println("Received message from Publisher " + "on channel: " + channel + " :: " + message );

			/*
			 * Calls the method asynchronously to handle the trigger
			 */
			TriggerUtil.handleTrigger(savedFnRegistry, new String(message.getBody()));

		};

		listenerContainer.addMessageListener(messageListener, new ChannelTopic(channel));
		channelListeners.put(savedFnRegistry.getFnId(), messageListener);

	}

	public void unsubscribeFromChannel(String channel, int fn_id) {

		System.out.println("*** Unsubscribing from channel: " + channel + " ***");

		MessageListener messageListener = channelListeners.remove(fn_id);

		if (messageListener != null) {
			listenerContainer.removeMessageListener(messageListener);
		}

	}
}
