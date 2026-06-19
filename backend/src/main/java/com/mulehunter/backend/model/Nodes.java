package com.mulehunter.backend.model;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;
import org.springframework.data.mongodb.core.index.Indexed;

/**
 * Maps to the "nodes" collection.
 *
 * CRITICAL: MongoDB stores fields in snake_case (node_id, is_fraud, in_degree …).
 * Every field that doesn't exactly match the Java camelCase auto-conversion
 * MUST have an explicit @Field("mongo_name") annotation, otherwise Spring Data
 * reads null and the field is silently ignored.
 */
@Document(collection = "nodes")
public class Nodes {

    @Id
    private String id;

    // MongoDB field: "node_id"
    @Field("node_id")
    @Indexed(unique = true)
    private Long nodeId;

    // MongoDB field: "is_fraud"  ← THIS was the bug — without @Field it was always null
    @Field("is_fraud")
    private String isFraud;

    // MongoDB field: "account_age_days"
    @Field("account_age_days")
    private String accountAgeDays;

    @Field("balance")
    private String balance;

    // MongoDB field: "in_out_ratio"
    @Field("in_out_ratio")
    private String inOutRatio;

    @Field("pagerank")
    private String pagerank;

    // MongoDB field: "tx_velocity"
    @Field("tx_velocity")
    private String txVelocity;

    // MongoDB field: "in_degree"
    @Field("in_degree")
    private String inDegree;

    // MongoDB field: "out_degree"
    @Field("out_degree")
    private String outDegree;

    // MongoDB field: "total_incoming"
    @Field("total_incoming")
    private String totalIncoming;

    // MongoDB field: "total_outgoing"
    @Field("total_outgoing")
    private String totalOutgoing;

    // MongoDB field: "risk_ratio"
    @Field("risk_ratio")
    private String riskRatio;

    // MongoDB field: "anomaly_score"
    @Field("anomaly_score")
    private Double anomalyScore;

    // MongoDB field: "is_anomalous"
    @Field("is_anomalous")
    private Integer isAnomalous;

    public Nodes() {}

    // ── Getters / Setters ─────────────────────────────────────────

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public Long getNodeId() { return nodeId; }
    public void setNodeId(Long v) { this.nodeId = v; }

    /**
     * Returns the raw is_fraud value from MongoDB ("0" or "1").
     * Use isFraudNode() in ModelEvaluationService to safely parse this.
     */
    public String getIsFraud() { return isFraud; }
    public void setIsFraud(String v) { this.isFraud = v; }

    public String getAccountAgeDays() { return accountAgeDays; }
    public void setAccountAgeDays(String v) { this.accountAgeDays = v; }

    public String getBalance() { return balance; }
    public void setBalance(String v) { this.balance = v; }

    public String getInOutRatio() { return inOutRatio; }
    public void setInOutRatio(String v) { this.inOutRatio = v; }

    public String getPagerank() { return pagerank; }
    public void setPagerank(String v) { this.pagerank = v; }

    public String getTxVelocity() { return txVelocity; }
    public void setTxVelocity(String v) { this.txVelocity = v; }

    public String getInDegree() { return inDegree; }
    public void setInDegree(String v) { this.inDegree = v; }

    public String getOutDegree() { return outDegree; }
    public void setOutDegree(String v) { this.outDegree = v; }

    public String getTotalIncoming() { return totalIncoming; }
    public void setTotalIncoming(String v) { this.totalIncoming = v; }

    public String getTotalOutgoing() { return totalOutgoing; }
    public void setTotalOutgoing(String v) { this.totalOutgoing = v; }

    public String getRiskRatio() { return riskRatio; }
    public void setRiskRatio(String v) { this.riskRatio = v; }

    public Double getAnomalyScore() { return anomalyScore; }
    public void setAnomalyScore(Double v) { this.anomalyScore = v; }

    public Integer getIsAnomalous() { return isAnomalous; }
    public void setIsAnomalous(Integer v) { this.isAnomalous = v; }
}