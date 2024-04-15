package com.iitb.faas.RegistryService;

import lombok.Data;

@Data
public class RegisterRequest {
	
    private String fnName;
    private String runtime;
    private String sourceCode;
    private String requirements;
    private String entryFn;
    private TriggerType triggerType;
    private EventType eventType;
    private String bucketId;
    
    private String bucket_id;
    
    public enum TriggerType {
        HTTP,
        CLOUD_STORAGE
    }

    public enum EventType {
        CREATE,
        INSERT,
        DELETE,
        MODIFY
    }
}


