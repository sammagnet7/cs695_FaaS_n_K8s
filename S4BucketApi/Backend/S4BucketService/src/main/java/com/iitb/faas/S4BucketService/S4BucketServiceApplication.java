package com.iitb.faas.S4BucketService;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

@EnableJpaRepositories
@SpringBootApplication
public class S4BucketServiceApplication {

	public static void main(String[] args) {
		SpringApplication.run(S4BucketServiceApplication.class, args);
	}

}
