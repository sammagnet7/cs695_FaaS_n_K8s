package com.iitb.faas.S4BucketService;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/s4")
public class BucketController {

	private String triggerMsg = "Designated Trigger is hit on Bucket: ";

	@Autowired
	private S4BucketService bucketService;

	@PostMapping("/createBucket/{bucketName}")
	public ResponseEntity<?> createBucket(@PathVariable String bucketName) {

		var createBucketResp = bucketService.createBucket(bucketName);

		String channel_name = bucketName + "_" + EventType.CREATE_BUCKET.toString() + "_" + "channel";
		bucketService.publishToChannel(channel_name, triggerMsg + bucketName);

		return createBucketResp;
	}

	@PostMapping("/uploadIntoBucket")
	public ResponseEntity<?> uploadIntoBucket(@RequestBody S4BucketRequest uploadRequest) {

		var uploadIntoBucketResp = bucketService.uploadIntoBucket(uploadRequest.getBucketName(),
				uploadRequest.getBase64Images());

		/*
		 * creating the Channel name string
		 */
		String channel_name = uploadRequest.getBucketName() + "_" + EventType.UPLOAD_INTO_BUCKET.toString() + "_"
				+ "channel";

		/*
		 * sending uploaded image IDs to the subscribers
		 */
		bucketService.publishToChannel(channel_name, "Inserted image IDs are: "+uploadIntoBucketResp.getBody().toString());

		return uploadIntoBucketResp;
	}

	@DeleteMapping("/deleteFromBucket")
	public ResponseEntity<?> deleteFromBucket(@RequestBody S4BucketRequest deleteRequest) {

		var deleteFromBucketResp = bucketService.deleteFromBucket(deleteRequest.getBucketName(),
				deleteRequest.getImageId());

		String channel_name = deleteRequest.getBucketName() + "_" + EventType.DELETE_FROM_BUCKET.toString() + "_"
				+ "channel";
		bucketService.publishToChannel(channel_name, triggerMsg + deleteRequest.getBucketName());

		return deleteFromBucketResp;
	}

	@DeleteMapping("/deleteBucket/{bucketName}")
	public ResponseEntity<?> deleteBucket(@PathVariable String bucketName) {

		var deleteBucketResp = bucketService.deleteBucket(bucketName);

		String channel_name = bucketName + "_" + EventType.DELETE_BUCKET.toString() + "_" + "channel";
		bucketService.publishToChannel(channel_name, triggerMsg + bucketName);

		return deleteBucketResp;
	}

	@GetMapping("/downloadImage/{bucketName}/{imageId}")
	public ResponseEntity<?> downloadImage(@PathVariable String bucketName, @PathVariable String imageId) {

		var imageDataBase64 = bucketService.getImageFromBucket(bucketName, Long.parseLong(imageId));

		String channel_name = bucketName + "_" + EventType.DOWNLOAD_IMAGE.toString() + "_" + "channel";
		bucketService.publishToChannel(channel_name, triggerMsg + bucketName);

		return imageDataBase64;
	}

	@GetMapping("/getAllFromBucket/{bucketName}")
	public ResponseEntity<?> getAllImagesInBucket(@PathVariable String bucketName) {

		return bucketService.getAllDataFromBucket(bucketName);

	}

}
