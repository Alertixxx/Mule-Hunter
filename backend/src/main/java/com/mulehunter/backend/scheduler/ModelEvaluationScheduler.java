package com.mulehunter.backend.scheduler;

import com.mulehunter.backend.service.ModelEvaluationService;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class ModelEvaluationScheduler {

    private final ModelEvaluationService evaluationService;

    public ModelEvaluationScheduler(ModelEvaluationService evaluationService) {
        this.evaluationService = evaluationService;
    }

    @Scheduled(cron = "0 0 2 * * ?") // runs daily at 2 AM
    public void runEvaluation() {
        System.out.println("⏰ Running scheduled model evaluation...");
        evaluationService.evaluateModels(false).subscribe();
    }
}