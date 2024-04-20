package com.iitb.faas.RegistryService;

import lombok.Data;

@Data
public class RegisterRequest_Downline {
	
    private String fnName;
    private String runtime;
    private String sourceCode;
    private String requirements;
    
}