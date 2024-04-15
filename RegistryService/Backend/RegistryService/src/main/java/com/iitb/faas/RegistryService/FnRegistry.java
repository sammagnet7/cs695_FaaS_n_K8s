package com.iitb.faas.RegistryService;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import lombok.Data;

@Data
@Entity
public class FnRegistry {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name= "fn_id")
    private int fnId;

    @Column(name = "fn_name", length = 255)
    private String fnName;

    @Column(name = "runtime", length = 255)
    private String runtime;

    @Column(name = "source_code", columnDefinition = "text")
    private String sourceCode;

    @Column(name = "requirements", columnDefinition = "text")
    private String requirements;

    @Column(name = "entry_fn", length = 1024)
    private String entryFn;
    
    @Column(name = "trigger_type", length = 255)
    private String triggerType;
    
    @Column(name = "event_type", length = 255)
    private String eventType;
    
    @Column(name = "bucket_id", length = 255)
    private String bucketId;
}
