package com.mulehunter.backend.DTO;

import java.util.List;

public class FraudExplanationDTO {

    private Long nodeId;
    private List<String> reasons;
    private String source;

    public FraudExplanationDTO() {}

    public Long getNodeId() { return nodeId; }
    public void setNodeId(Long nodeId) { this.nodeId = nodeId; }

    public List<String> getReasons() { return reasons; }
    public void setReasons(List<String> reasons) { this.reasons = reasons; }

    public String getSource() { return source; }
    public void setSource(String source) { this.source = source; }
}
