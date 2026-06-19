package com.mulehunter.backend.controller;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import com.mulehunter.backend.model.AnomalyScore;
import com.mulehunter.backend.model.FraudExplanation;
import com.mulehunter.backend.repository.*;
import com.mulehunter.backend.DTO.NodeAnalyticsResponse;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/backend/api/visual/node")
public class NodeAnalyticsController {

    private final NodeEnrichedRepository nodeRepo;
    private final AnomalyScoreRepository anomalyRepo;
    private final ShapExplanationRepository shapRepo;
    private final FraudExplanationRepository fraudRepo;

    public NodeAnalyticsController(
            NodeEnrichedRepository nodeRepo,
            AnomalyScoreRepository anomalyRepo,
            ShapExplanationRepository shapRepo,
            FraudExplanationRepository fraudRepo) {

        this.nodeRepo = nodeRepo;
        this.anomalyRepo = anomalyRepo;
        this.shapRepo = shapRepo;
        this.fraudRepo = fraudRepo;
    }

    @GetMapping("/{nodeId}/full")
public Mono<NodeAnalyticsResponse> getFull(@PathVariable Long nodeId) {

    // Mono.zip fails completely if ANY of its sources completes empty.
    // Nodes that were never scored have no anomaly/fraud docs yet, so we
    // must provide empty-object fallbacks — not Mono.empty() — for those.
    return Mono.zip(
            nodeRepo.findByNodeId(nodeId),
            anomalyRepo.findByNodeId(nodeId).defaultIfEmpty(new AnomalyScore()),
            shapRepo.findByNodeId(nodeId).collectList(),
            fraudRepo.findByNodeId(nodeId).defaultIfEmpty(new FraudExplanation())
    ).map(t -> {

        NodeAnalyticsResponse r = new NodeAnalyticsResponse();
        r.setFeatures(t.getT1());
        r.setAnomaly(t.getT2());
        r.setShap(t.getT3());
        r.setReasons(t.getT4());

        return r;
    });
}
}