package com.mulehunter.backend.websocket;

public class FraudAlertEvent {

    private String accountId;
    private double riskScore;
    private String verdict;

    public FraudAlertEvent(String accountId, double riskScore, String verdict) {
        this.accountId = accountId;
        this.riskScore = riskScore;
        this.verdict = verdict;
    }

    public String getAccountId() {
        return accountId;
    }

    public double getRiskScore() {
        return riskScore;
    }

    public String getVerdict() {
        return verdict;
    }
}
