package com.mulehunter.backend.controller;

import java.util.List;
import java.time.Instant;

import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

import com.mulehunter.backend.model.FraudExplanation;
import com.mulehunter.backend.DTO.FraudExplanationDTO;
import com.mulehunter.backend.repository.FraudExplanationRepository;

import reactor.core.publisher.Mono;
import reactor.core.publisher.Flux;

@RestController
@RequestMapping("/backend/api/visual/fraud-explanations")
public class FraudExplanationController {

    private final FraudExplanationRepository repository;

    public FraudExplanationController(FraudExplanationRepository repository) {
        this.repository = repository;
    }

    @PostMapping("/batch")
    public Mono<String> saveBatch(@RequestBody List<FraudExplanationDTO> payload) {

        return Flux.fromIterable(payload)
                .flatMap(dto -> repository.findByNodeId(dto.getNodeId())
                        .defaultIfEmpty(new FraudExplanation())
                        .flatMap(existing -> {
                            existing.setNodeId(dto.getNodeId());
                            existing.setReasons(dto.getReasons());
                            existing.setSource(dto.getSource());
                            existing.setUpdatedAt(Instant.now());
                            return repository.save(existing);
                        }))
                .then(Mono.just("Fraud explanations stored successfully"));
    }
}
