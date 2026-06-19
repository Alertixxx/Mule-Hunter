package com.mulehunter.backend.service;

import java.time.Instant;

import org.springframework.stereotype.Service;

import com.mulehunter.backend.model.NodeEnriched;
import com.mulehunter.backend.repository.NodeEnrichedRepository;

import reactor.core.publisher.Mono;

@Service
public class NodeEnrichedService {

    private final NodeEnrichedRepository repository;

    public NodeEnrichedService(NodeEnrichedRepository repository) {
        this.repository = repository;
    }

    public Mono<Void> handleOutgoing(Long nodeId, double amount) {

        return repository.findByNodeId(nodeId)
                .defaultIfEmpty(createNew(nodeId))
                .flatMap(node -> {
                    node.setOutDegree(node.getOutDegree() + 1);
                    node.setTotalOutgoing(node.getTotalOutgoing() + amount);
                    recalcRiskRatio(node);
                    node.setUpdatedAt(Instant.now());
                    return repository.save(node);
                })
                .then();
    }

    public Mono<Void> handleIncoming(Long nodeId, double amount) {

        return repository.findByNodeId(nodeId)
                .defaultIfEmpty(createNew(nodeId))
                .flatMap(node -> {
                    node.setInDegree(node.getInDegree() + 1);
                    node.setTotalIncoming(node.getTotalIncoming() + amount);
                    recalcRiskRatio(node);
                    node.setUpdatedAt(Instant.now());
                    return repository.save(node);
                })
                .then();
    }


    private NodeEnriched createNew(Long nodeId) {
        NodeEnriched node = new NodeEnriched();
        node.setNodeId(nodeId);
        node.setInDegree(0);
        node.setOutDegree(0);
        node.setTotalIncoming(0.0);
        node.setTotalOutgoing(0.0);
        node.setRiskRatio(1.0);
        node.setTxVelocity(0);
        node.setAccountAgeDays(0);
        node.setBalance(0.0);
        node.setUpdatedAt(Instant.now());
        return node;
    }

    private void recalcRiskRatio(NodeEnriched node) {
        if (node.getTotalIncoming() == 0) {
            node.setRiskRatio(1.0);
        } else {
            node.setRiskRatio(
                node.getTotalOutgoing() / node.getTotalIncoming()
            );
        }
    }
}
