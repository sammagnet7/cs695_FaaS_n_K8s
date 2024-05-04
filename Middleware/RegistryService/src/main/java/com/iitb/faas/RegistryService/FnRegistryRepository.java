package com.iitb.faas.RegistryService;

import org.springframework.data.jpa.repository.JpaRepository;

public interface FnRegistryRepository extends JpaRepository<FnRegistry, Integer> {
	
    FnRegistry findByFnName(String fnName);

}
