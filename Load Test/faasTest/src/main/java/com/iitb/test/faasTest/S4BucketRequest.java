package com.iitb.test.faasTest;

import java.util.List;

import lombok.Data;

@Data
public class S4BucketRequest {
	private String bucketName;
    private List<String> base64Images;
}
