package com.iitb.faas.S4BucketService;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.BadSqlGrammarException;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class S4BucketService {

	@Autowired
	private JdbcTemplate jdbcTemplate;

	@Autowired
	private RedisPublisher redisPublisher;

	@Transactional
	public ResponseEntity<?> createBucket(String bucketName) {

		try {
			jdbcTemplate.execute("CREATE TABLE " + bucketName
					+ "(file_id SERIAL PRIMARY KEY, image BYTEA, additional_info_type varchar, additional_info text )");

			return ResponseEntity.ok().body("Bucket created successfully.");
		} catch (Exception e) {
			e.printStackTrace();
			return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(e.getCause().toString());
		}
	}

	@Transactional
	public ResponseEntity<?> uploadIntoBucket(String bucketName, List<String> base64images) {

		try {
			List<String> insertedImageIds = new ArrayList<>();

			List<byte[]> images = base64ToBytes(base64images);

			for (byte[] imageData : images) {

				jdbcTemplate.update(
						"INSERT INTO " + bucketName
								+ " (image, additional_info, additional_info_type) VALUES (?, ?, ?)",
						imageData, "EMPTY", "TEXT");

				String fileId = jdbcTemplate.queryForObject("SELECT LASTVAL() AS VARCHAR", String.class);
				insertedImageIds.add(fileId);
			}
			return ResponseEntity.ok(insertedImageIds);
		} catch (Exception e) {
			e.printStackTrace();
			return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Failed to upload images.");
		}
	}

	@Transactional
	public ResponseEntity<?> deleteFromBucket(String bucketName, String imageId) {

		try {
			int deletedRowCount = jdbcTemplate.update("DELETE FROM " + bucketName + " WHERE file_id = " + imageId);
			if (deletedRowCount > 0) {
				return ResponseEntity.ok().body("Image deleted successfully.");
			} else {
				return ResponseEntity.status(HttpStatus.NOT_FOUND)
						.body("Image with image id: " + imageId + " in bucket: " + bucketName + " does not exist.");
			}
		} catch (Exception e) {
			e.printStackTrace();
			return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Failed to delete image.");
		}
	}

	@Transactional
	public ResponseEntity<?> deleteBucket(String bucketName) {

		try {
			jdbcTemplate.execute("DROP TABLE IF EXISTS " + bucketName);
			return ResponseEntity.ok().body("Bucket deleted successfully.");

		} catch (Exception e) {
			e.printStackTrace();

			return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Failed to delete bucket.");
		}
	}

	@Transactional(readOnly = true)
	public ResponseEntity<?> getImageFromBucket(String bucketName, Long imageId) {

		try {
			byte[] imageData = jdbcTemplate.query("SELECT image FROM " + bucketName + " WHERE file_id = ?",
					(ResultSet rs) -> {
						if (rs.next()) {
							return rs.getBytes("image");
						} else {
							throw new SQLException("Image data not found");
						}
					}, imageId);

			return ResponseEntity.ok(bytesToBase64(imageData));

		} catch (Exception e) {
			e.printStackTrace();
			return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
					.body("Failed to fetch particular image from bucket.");

		}
	}

	@Transactional(readOnly = true)
	public ResponseEntity<?> getAllDataFromBucket(String bucketName) {
		try {
			List<Map<String, Object>> dataList = jdbcTemplate.queryForList("SELECT * FROM " + bucketName);
			return ResponseEntity.ok(dataList);
		} catch (BadSqlGrammarException e) {
			return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("The specified bucket does not exist.");
		} catch (Exception e) {
			e.printStackTrace();
			return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Failed to fetch data from bucket.");
		}
	}

	public void publishToChannel(String channel, String msg) {

		redisPublisher.publishMessage(channel, msg);
	}

	private List<byte[]> base64ToBytes(List<String> base64Images) {
		List<byte[]> images = new ArrayList<>();
		for (String base64Image : base64Images) {
			byte[] imageData = Base64.getDecoder().decode(base64Image);
			images.add(imageData);
		}
		return images;
	}

	private String bytesToBase64(byte[] ImagesBytes) {
		String base64Image = Base64.getEncoder().encodeToString(ImagesBytes);
		return base64Image;
	}

}
