package com.iitb.faas.S4BucketService;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class S4BucketService {

	@Autowired
	private JdbcTemplate jdbcTemplate;
	
	@Autowired
	private RedisPublisher redisPublisher;

//    public YourBusinessService(JedisPublisher jedisPublisher) {
//        this.jedisPublisher = jedisPublisher;
//    }

	@Transactional
	public ResponseEntity<?> createBucket(String bucketName) {

		try {
			jdbcTemplate.execute("CREATE TABLE IF NOT EXISTS " + bucketName
					+ "(file_id SERIAL PRIMARY KEY, image BYTEA, status VARCHAR(255) )");

			return ResponseEntity.ok().body("Bucket created successfully.");
		} catch (Exception e) {
			return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Failed to create bucket.");
		}
	}

	@Transactional
	public ResponseEntity<?> uploadIntoBucket(String bucketName, List<String> base64images) {

		try {
			List<String> insertedImageIds = new ArrayList<>();

			List<byte[]> images = base64ToBytes(base64images);

			for (byte[] imageData : images) {

				jdbcTemplate.update("INSERT INTO " + bucketName + " (image, status) VALUES (?, ?)", imageData,
						"ACTIVE");

				String fileId = jdbcTemplate.queryForObject("SELECT LASTVAL() AS VARCHAR", String.class);
				insertedImageIds.add(fileId);
			}
			return ResponseEntity.ok(insertedImageIds);
		} catch (Exception e) {
			return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Failed to upload images.");
		}
	}

	@Transactional
	public ResponseEntity<?> deleteFromBucket(String bucketName, String imageId) {

		try {
			jdbcTemplate.update("DELETE FROM " + bucketName + " WHERE file_id = "+ imageId);
			return ResponseEntity.ok().body("Image deleted successfully.");

		} catch (Exception e) {
			return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Failed to delete image.");
		}
	}

	@Transactional
	public ResponseEntity<?> deleteBucket(String bucketName) {

		try {
			jdbcTemplate.execute("DROP TABLE IF EXISTS " + bucketName);
			return ResponseEntity.ok().body("Bucket deleted successfully.");

		} catch (Exception e) {
			return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Failed to delete bucket.");
		}
	}

	public String getImageDataAsBase64(String bucketName, Long imageId) {

		try {
			byte[] imageData = jdbcTemplate.query("SELECT image FROM " + bucketName + " WHERE file_id = ?",
					(ResultSet rs) -> {
						if (rs.next()) {
							return rs.getBytes("image");
						} else {
							throw new SQLException("Image data not found");
						}
					}, imageId);

			return base64ToBytes(imageData);

		} catch (Exception e) {
			e.printStackTrace();
			return null;
		}
	}

	private List<byte[]> base64ToBytes(List<String> base64Images) {
		List<byte[]> images = new ArrayList<>();
		for (String base64Image : base64Images) {
			byte[] imageData = Base64.getDecoder().decode(base64Image);
			images.add(imageData);
		}
		return images;
	}

	private String base64ToBytes(byte[] ImagesBytes) {
		String base64Image = Base64.getEncoder().encodeToString(ImagesBytes);
		return base64Image;
	}
	
	 public void publishToChannel(String channel, String msg) {
	        
	        redisPublisher.publishMessage(channel, msg);
	    }

}
