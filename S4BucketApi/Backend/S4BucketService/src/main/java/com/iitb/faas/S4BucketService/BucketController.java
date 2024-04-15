package com.iitb.faas.S4BucketService;

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

	final String MSG = "Designated Trigger is hit";

	@Autowired
	private S4BucketService bucketService;

	@PostMapping("/createBucket/{bucketName}")
	public ResponseEntity<?> createBucket(@PathVariable String bucketName) {

		var createBucketResp = bucketService.createBucket(bucketName);

		String channel_name = bucketName + "_" + EventType.CREATE_BUCKET.toString() + "_" + "channel";
		bucketService.publishToChannel(channel_name, MSG);

		return createBucketResp;
	}

	@PostMapping("/uploadIntoBucket")
	public ResponseEntity<?> uploadIntoBucket(@RequestBody S4BucketRequest uploadRequest) {

		var uploadIntoBucketResp = bucketService.uploadIntoBucket(uploadRequest.getBucketName(),
				uploadRequest.getBase64Images());

		String channel_name = uploadRequest.getBucketName() + "_" + EventType.UPLOAD_INTO_BUCKET.toString() + "_"
				+ "channel";
		bucketService.publishToChannel(channel_name, MSG);

		return uploadIntoBucketResp;
	}

	@DeleteMapping("/deleteFromBucket")
	public ResponseEntity<?> deleteFromBucket(@RequestBody S4BucketRequest deleteRequest) {

		var deleteFromBucketResp = bucketService.deleteFromBucket(deleteRequest.getBucketName(),
				deleteRequest.getImageId());

		String channel_name = deleteRequest.getBucketName() + "_" + EventType.DELETE_FROM_BUCKET.toString() + "_"
				+ "channel";
		bucketService.publishToChannel(channel_name, MSG);

		return deleteFromBucketResp;
	}

	@DeleteMapping("/deleteBucket/{bucketName}")
	public ResponseEntity<?> deleteBucket(@PathVariable String bucketName) {

		var deleteBucketResp = bucketService.deleteBucket(bucketName);

		String channel_name = bucketName + "_" + EventType.DELETE_BUCKET.toString() + "_" + "channel";
		bucketService.publishToChannel(channel_name, MSG);

		return deleteBucketResp;
	}

	@GetMapping("/downloadImage")
	public ResponseEntity<?> downloadImage(@RequestBody S4BucketRequest downloadRequest) {

		String imageDataBase64 = bucketService.getImageDataAsBase64(downloadRequest.getBucketName(),
				Long.parseLong(downloadRequest.getImageId()));

		String channel_name = downloadRequest.getBucketName() + "_" + EventType.DOWNLOAD_IMAGE.toString() + "_"
				+ "channel";
		bucketService.publishToChannel(channel_name, MSG);

		if (imageDataBase64 != null) {
			return ResponseEntity.ok(imageDataBase64);
		} else {
			return ResponseEntity.status(HttpStatus.NOT_FOUND).body("Image not found");
		}
	}

}
