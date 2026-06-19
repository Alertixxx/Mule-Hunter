package com.mulehunter.backend.DTO;

public class MetricsResponse {

    public ModelMetrics combined;
    public ModelMetrics gnn;
    public ModelMetrics eif;

    // Scientific / Offline metrics from ML engines
    public OfflineMetrics offlineGnn;
    public OfflineMetrics offlineEif;

    public static class ModelMetrics {
        public double precision;
        public double recall;
        public double f1Score;
        public double accuracy;
        public double fpr;
        public double fnr;
        public double auc;
    }

    public static class OfflineMetrics {
        public double accuracy;
        public double precision;
        public double recall;
        public double f1;
        public double auc;
        public double threshold;
    }
}