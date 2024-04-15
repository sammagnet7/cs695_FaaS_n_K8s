package com.iitb.faas.RegistryService;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
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
	public ResponseEntity<String> registerFunction(@RequestBody RegisterRequest registerRequest) {
		fnRegistryService.registerFunction(registerRequest);
		return new ResponseEntity<>("Function registered successfully", HttpStatus.CREATED);
	}

	@DeleteMapping("/deregisterFunction/{fnId}")
	public String unsubscribeFunction(@PathVariable int fnId) {
		
		System.out.println("deregistering function with function id: "+fnId);
		
		fnRegistryService.deregisterFunction(fnId);
		
		return "Deregistered function with fn_id: " + fnId;
	}
}
