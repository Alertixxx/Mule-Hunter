package com.mulehunter.backend.repository;

import org.springframework.data.mongodb.repository.ReactiveMongoRepository;
import reactor.core.publisher.Mono;
import com.mulehunter.backend.model.FraudExplanation;

public interface FraudExplanationRepository extends ReactiveMongoRepository<FraudExplanation, String>{
    Mono<FraudExplanation> findByNodeId(Long nodeId);
}