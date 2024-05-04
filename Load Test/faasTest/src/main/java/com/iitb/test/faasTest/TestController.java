package com.iitb.test.faasTest;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;
import java.util.Random;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicInteger;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClient.ResponseSpec;

import reactor.core.Disposable;

@RequestMapping("/testfaas")
@RestController
class TestController {

	@Autowired
	private WebClient.Builder webClientBuilder;

	@Value("${register.function.url}")
	private String fnRegApi;

	@Value("${deregister.function.url}")
	private String fnDeRegApi;

	@Value("${bucket.create.url}")
	private String createApi;

	@Value("${bucket.delete.url}")
	private String deleteApi;

	@Value("${bucket.upload.url}")
	private String uploadApi;

	@Value("${bucket.status.url}")
	private String statusApi;


	@Value("${interval.poll.ms}")
	private String poll_interval_MS;

	private final int WAIT_MS = 3000;
	private final int IMAGE_ARRAY_LEN = 10;

	private static List<File> imageFiles;

	@GetMapping("/test")
	public CompletableFuture<String> testEndpoint() {
		// Simulate some processing time
		return CompletableFuture.supplyAsync(() -> {
			try {
				Thread.sleep(1000); // Simulate processing time

			} catch (InterruptedException e) {
				Thread.currentThread().interrupt();
			}
			return "Test Successful";
		});
	}

	@PostMapping("/runTest")
	public String runTest(@RequestBody TestFaasRequest testReq) {
		
		try {
			deRegisterFunction(testReq.getFnName());
		} catch(Exception e) {
			System.out.println("Was trying to remove stale Function of earlier test cases");
		}

		// Registering function as a part of which the event will be triggered
		registerFunction(testReq);

		// Starting the timer from this point as part of performance testing of the FAAS
		// application
		Instant startTime = Instant.now();

		// Create the bucket before starting the test loop
		createBucket(testReq.getBucketName());

		int iterations = testReq.getLoadCount() / IMAGE_ARRAY_LEN; // Calculate number of iterations needed
		AtomicInteger successfulReqs = new AtomicInteger(0);

		// Create a CountDownLatch with the count equal to the number of requests
		CountDownLatch latch = new CountDownLatch(iterations);
		List<Disposable> disposables = new ArrayList<>();

		try {
			Thread.sleep(3000); // Wait for 3 seconds to allow all requests to be settled
		} catch (InterruptedException e) {
			Thread.currentThread().interrupt();
			System.err.println("Interrupted while sleeping: " + e.getMessage());
		}

		System.out.println("Test Run Started");

		for (int i = 0; i < iterations; i++) {

			// Create pay-load using S4BucketRequest
			S4BucketRequest request = buildUploadIntoBucketRequest(IMAGE_ARRAY_LEN, testReq.getBucketName(),
					testReq.getResourceFolderPath());

			Disposable disposable = webClientBuilder.build().post() //
					.uri(uploadApi) //
					.header(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE) //
					.body(BodyInserters.fromValue(request)).retrieve().bodyToMono(String.class).subscribe( //
							result -> {
								System.out.println("Request completed: " + result);
								successfulReqs.incrementAndGet(); // Increment the AtomicInteger
								latch.countDown();
							}, ex -> {
								System.err.println("Request failed: " + ex.getMessage());
								latch.countDown();
							});

			disposables.add(disposable); // Store the disposable in the list
		}

		// Wait until all requests have completed
		try {
			latch.await(); // Block until latch count reaches zero

		} catch (InterruptedException e) {
			Thread.currentThread().interrupt();
			System.err.println("Interrupted while waiting for requests to complete: " + e.getMessage());
		}

		// Dispose of the subscription once all requests have completed
		for (Disposable disposable : disposables) {
			if (disposable != null) {
				disposable.dispose();
			}
		}

		try {
			Thread.sleep(WAIT_MS); // Wait for 3 seconds to allow all requests to be settled
		} catch (InterruptedException e) {
			Thread.currentThread().interrupt();
			System.err.println("Interrupted while sleeping: " + e.getMessage());
		}

		System.out.println("Status check Started");

		StatusResponse response = getStatusCheck(testReq.getFnName());
		System.out.println("resp: " + response);

		while (response == null || response.getStatus() == null
				|| (!response.getStatus().equals(Status.SUCCESS.toString())
						&& !response.getStatus().equals(Status.FAILED.toString()))) {
			try {
				Thread.sleep(Long.parseLong(poll_interval_MS)); // Wait before making the next status check

				response = getStatusCheck(testReq.getFnName());
				System.out.println("resp: " + response);

			} catch (InterruptedException e) {
				Thread.currentThread().interrupt();
				System.err.println("Interrupted while waiting for status check: " + e.getMessage());
			}
		}

		Instant finishTime = response != null ? Instant.parse(response.getFinishTime()) : null;

		// Log start time and completion time w.r.t the load
		logTime(startTime, finishTime, (successfulReqs.get() * IMAGE_ARRAY_LEN), testReq.getResourceFolderPath(), testReq.getFnName());

		System.out.println("Test Run Finished");

		deleteBucket(testReq.getBucketName());
		deRegisterFunction(testReq.getFnName());

		return "Test run successful. Please check test output in the below path: " + testReq.getResourceFolderPath();

	}

	public void registerFunction(TestFaasRequest testReq) {

		// Create local variables for payload JSON
		String fnName = testReq.getFnName();
		String bucketName = testReq.getBucketName();
		String runtime = testReq.getRuntime();
		String sourceCode = testReq.getSourceCode();
		String requirements = testReq.getRequirements();
		String entryFn = testReq.getEntryFn();
		String triggerType = testReq.getTriggerType();
		String eventType = testReq.getEventType();
		String replicaLimit = testReq.getReplicaLimit();
		String cpuMax = testReq.getCpuMax();
		String memoryMax = testReq.getMemoryMax();

		// Create the payload string
		String payload = "{" + "\"fnName\": \"" + fnName + "\"," + "\"runtime\": \"" + runtime + "\","
				+ "\"sourceCode\": \"" + sourceCode + "\"," + "\"requirements\": \"" + requirements + "\","
				+ "\"entryFn\": \"" + entryFn + "\"," + "\"triggerType\": \"" + triggerType + "\","
				+ "\"eventType\": \"" + eventType + "\"," + "\"bucketName\": \"" + bucketName + "\","
				+ "\"replicaLimit\": \"" + replicaLimit + "\"," + "\"cpuMax\": \"" + cpuMax + "\","
				+ "\"memoryMax\": \"" + memoryMax + "\"" + "}";
		// Set up WebClient
		WebClient webClient = WebClient.create();

		// Send the POST request synchronously
		ResponseEntity<Void> responseEntity = webClient.post().uri(fnRegApi)
				.header(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE).bodyValue(payload).retrieve()
				.toBodilessEntity().block();

		// Check the response status
		if (responseEntity != null && responseEntity.getStatusCode().is2xxSuccessful()) {
			System.out.println("Function registration successful");
		} else {
			System.err.println("Function registration failed");
		}
	}

	public void deRegisterFunction(String fnName) {

		// Set up WebClient
		WebClient webClient = WebClient.create();

		// Send the DELETE request synchronously
		ResponseEntity<Void> responseEntity = webClient.delete().uri(fnDeRegApi + "/" + fnName).retrieve()
				.toBodilessEntity().block();

		// Check the response status
		if (responseEntity != null && responseEntity.getStatusCode().is2xxSuccessful()) {
			System.out.println("Function deregistration successful");
		} else {
			System.err.println("Function deregistration failed");
		}
	}

	private void createBucket(String bucketName) {

		ResponseSpec responseSpec = webClientBuilder.build().post().uri(createApi + "/" + bucketName).retrieve();

		String response = responseSpec.bodyToMono(String.class).block();
		if (response != null) {
			System.out.println(response);
		} else {
			System.err.println("Failed to create bucket: Empty response");
		}
	}

	public void deleteBucket(String bucketName) {

		// Create WebClient
		WebClient webClient = WebClient.create();

		webClient.delete().uri(deleteApi + "/" + bucketName).retrieve().bodyToMono(Void.class).block();

	}

	private S4BucketRequest buildUploadIntoBucketRequest(int imageCount, String bucketName, String resourceFolderPath) {

		// Read images from resource folder
		List<File> imageFiles = readImagesFromResourceFolder(resourceFolderPath);

		// Randomly select 10 images
		List<File> selectedImages = selectRandomImages(imageFiles, imageCount);

		// Convert selected images to base64 strings
		List<String> base64Images = convertImagesToBase64(selectedImages);

		// Create S4BucketRequest object
		S4BucketRequest request = new S4BucketRequest();
		request.setBucketName(bucketName);
		request.setBase64Images(base64Images);

		return request;
	}

	private List<File> readImagesFromResourceFolder(String resourceFolderPath) {

		if (imageFiles != null) {
			return imageFiles;
		}

		String imagePath = resourceFolderPath + "/static/images/";
		File resourceFolder = new File(imagePath);
		File[] files = resourceFolder.listFiles();

		if (files != null) {

			imageFiles = new ArrayList<>();
			for (File file : files) {
				if (file.isFile() && file.getName().endsWith(".png")) {
					imageFiles.add(file);
				}
			}
		}
		return imageFiles;
	}

	private List<File> selectRandomImages(List<File> imageFiles, int count) {

		List<File> selectedImages = new ArrayList<>();
		Random random = new Random();
		for (int i = 0; i < count; i++) {
			int index = random.nextInt(imageFiles.size());
			selectedImages.add(imageFiles.get(index));
		}
		return selectedImages;
	}

	private List<String> convertImagesToBase64(List<File> imageFiles) {

		List<String> base64Images = new ArrayList<>();
		for (File file : imageFiles) {
			try {
				byte[] fileContent = java.nio.file.Files.readAllBytes(file.toPath());
				String base64String = Base64.getEncoder().encodeToString(fileContent);
				base64Images.add(base64String);
			} catch (Exception e) {
				System.err.println("Failed to read image file: " + file.getName());
			}
		}
		return base64Images;
	}

	private StatusResponse getStatusCheck(String functionName) {

		WebClient webClient = webClientBuilder.build();

		return webClient.get().uri(statusApi + "/" + functionName).retrieve().bodyToMono(StatusResponse.class).block();
	}

	private void logTime(Instant startTime, Instant finishTime, int loadCount, String resourceFolderPath, String fnName) {

		String logFileName = "/logs/"+fnName+".csv";
		String logFilePath = resourceFolderPath + logFileName;

		File file = new File(logFilePath);

		try (BufferedWriter writer = new BufferedWriter(new FileWriter(file, true))) {

			if (file.length() == 0) {
				try {
					writer.write("Load,Start Time,Finish Time,Response Time (sec),Throughput (per sec)");
					writer.newLine();

				} catch (IOException e) {
					System.err.println("An error occurred: " + e.getMessage());
				}
			}

			Duration duration = Duration.between(startTime, finishTime);

			long durationInSeconds = duration.getSeconds();

			double responseTimePerLoad = (double) durationInSeconds / loadCount;
			double throughput = (double) loadCount / durationInSeconds;

			writer.write(loadCount + "," //
					+ startTime.atZone(ZoneId.of("Asia/Kolkata")).format(DateTimeFormatter.ISO_OFFSET_DATE_TIME) + "," //
					+ finishTime.atZone(ZoneId.of("Asia/Kolkata")).format(DateTimeFormatter.ISO_OFFSET_DATE_TIME) + "," //
					+ responseTimePerLoad + "," + throughput);

			writer.newLine();
		} catch (IOException e) {
			System.err.println("Failed to write log: " + e.getMessage());
		}
	}
}