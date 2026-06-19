package com.mulehunter.backend.model;

import java.time.Instant;
import java.util.List;
import java.util.Map;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

@Document(collection = "shap_explanations")
public class ShapExplanation {

    @Id
    private String id;

    private Long nodeId;
    private double anomalyScore;
    private List<Map<String, Object>> topFactors;
    private String model;
    private String source;
    private Instant updatedAt;

    public ShapExplanation() {
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public Long getNodeId() {
        return nodeId;
    }

    public void setNodeId(Long nodeId) {
        this.nodeId = nodeId;
    }

    public double getAnomalyScore() {
        return anomalyScore;
    }

    public void setAnomalyScore(double anomalyScore) {
        this.anomalyScore = anomalyScore;
    }

    public List<Map<String, Object>> getTopFactors() {
        return topFactors;
    }

    public void setTopFactors(List<Map<String, Object>> topFactors) {
        this.topFactors = topFactors;
    }

    public String getModel() {
        return model;
    }

    public void setModel(String model) {
        this.model = model;
    }

    public String getSource() {
        return source;
    }

    public void setSource(String source) {
        this.source = source;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(Instant updatedAt) {
        this.updatedAt = updatedAt;
    }
}
