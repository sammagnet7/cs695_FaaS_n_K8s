package com.iitb.faas.S4BucketService;

import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Component;

@Component
public class RedisPublisher {

    private final RedisTemplate redisTemplate;

    public RedisPublisher(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    public void publishMessage(String channel, String message) {
    	System.out.println("*** Publishing to channel: "+ channel +" ***");
        redisTemplate.convertAndSend(channel, message);
    }
}