package com.iitb.faas.S4BucketService;

import java.util.List;

import lombok.Data;

@Data
public class S4BucketRequest {
	
	private String bucketName;
    private List<String> base64Images;
    private String imageId;
}


