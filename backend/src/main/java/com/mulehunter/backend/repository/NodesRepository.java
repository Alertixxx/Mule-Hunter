package com.mulehunter.backend.repository;

import com.mulehunter.backend.model.Nodes;
import org.springframework.data.mongodb.repository.ReactiveMongoRepository;
import reactor.core.publisher.Mono;

public interface NodesRepository extends ReactiveMongoRepository<Nodes, String> {

    Mono<Nodes> findByNodeId(Long nodeId);
}