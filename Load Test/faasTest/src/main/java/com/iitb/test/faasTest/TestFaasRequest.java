package com.iitb.test.faasTest;

import lombok.Data;

@Data
public class TestFaasRequest {
	
	private int loadCount;
	private String resourceFolderPath;
	
	private String fnName;
    private String bucketName; 
	private String runtime;
	private String sourceCode;
	private String requirements;
	private String entryFn;
	private String triggerType;
	private String eventType;
	private String replicaLimit;
	private String cpuMax;
	private String memoryMax;
}
