package com.iitb.faas.RegistryService;

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
@RequestMapping("/faas")
public class FnRegistryController {

	private final FnRegistryService fnRegistryService;

	@Autowired
	public FnRegistryController(FnRegistryService fnRegistryService) {
		this.fnRegistryService = fnRegistryService;
	}

	@PostMapping("/registerFunction")
	public ResponseEntity<?> registerFunction(@RequestBody RegisterRequest registerRequest) {

		fnRegistryService.registerFunction(registerRequest);

		return new ResponseEntity<>("Function registered successfully", HttpStatus.CREATED);
	}

	@DeleteMapping("/deregisterFunction/{fnName}")
	public ResponseEntity<?> unsubscribeFunction(@PathVariable String fnName) {

		System.out.println("deregistering function : " + fnName);

		fnRegistryService.deregisterFunction(fnName);

		return new ResponseEntity<>("Deregistered function : " + fnName, HttpStatus.OK);

	}

	@GetMapping("/getAllFunctions")
	public ResponseEntity<?> getAllFunctions() {
		List<FnRegistry> functions = fnRegistryService.getAllFunctions();
		return new ResponseEntity<>(functions, HttpStatus.OK);
	}
}
