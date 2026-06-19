package com.mulehunter.backend.repository;

import org.springframework.data.mongodb.repository.ReactiveMongoRepository;
import com.mulehunter.backend.model.ShapExplanation;
import reactor.core.publisher.Flux;

public interface ShapExplanationRepository
        extends ReactiveMongoRepository<ShapExplanation, String> {

    Flux<ShapExplanation> findByNodeId(Long nodeId);
}
