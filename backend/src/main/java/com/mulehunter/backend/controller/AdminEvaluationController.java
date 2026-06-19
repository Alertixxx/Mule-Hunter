package com.mulehunter.backend.controller;

import com.mulehunter.backend.DTO.MetricsResponse;
import com.mulehunter.backend.DTO.StatsResponse;
import com.mulehunter.backend.service.ModelEvaluationService;
import com.mulehunter.backend.service.StatsService;
import com.mulehunter.backend.service.MetricsPdfService;

import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.ContentDisposition;
import org.springframework.http.HttpStatus;

import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;

import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;

@RestController
@RequestMapping("/api/admin")
public class AdminEvaluationController {

    private final ModelEvaluationService evaluationService;
    private final StatsService statsService;
    private final MetricsPdfService metricsPdfService;

    public AdminEvaluationController(
            ModelEvaluationService evaluationService,
            StatsService statsService,
            MetricsPdfService metricsPdfService
    ) {
        this.evaluationService = evaluationService;
        this.statsService      = statsService;
        this.metricsPdfService = metricsPdfService;
    }

    /**
     * GET /api/admin/evaluate-models
     */
    @GetMapping("/evaluate-models")
    public Mono<MetricsResponse> evaluateModels(
            @RequestParam(value = "rescore", defaultValue = "false") boolean rescore
    ) {
        return evaluationService.evaluateModels(rescore);
    }

    /**
     * GET /api/admin/stats
     */
    @GetMapping("/stats")
    public Mono<StatsResponse> getStats() {
        return statsService.getStats();
    }

    /**
     * GET /api/admin/evaluate-models/download
     */
    @GetMapping("/evaluate-models/download")
    public Mono<ResponseEntity<byte[]>> downloadMetricsPdf() {
        return evaluationService.evaluateModels(false).flatMap(metrics -> {
            try {
                byte[] pdf = metricsPdfService.generate(metrics);

                String ts = ZonedDateTime.now(ZoneOffset.UTC)
                        .format(DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss"));
                String fn = "mule-hunter-metrics-" + ts + ".pdf";

                ContentDisposition cd = ContentDisposition.builder("attachment")
                        .filename(fn)
                        .build();

                HttpHeaders h = new HttpHeaders();
                h.setContentDisposition(cd);
                h.setContentType(MediaType.APPLICATION_PDF);
                h.setCacheControl("no-cache, no-store, must-revalidate");
                h.setPragma("no-cache");
                h.add("X-Content-Type-Options", "nosniff");

                return Mono.just(ResponseEntity.ok().headers(h).body(pdf));
            } catch (Exception e) {
                return Mono.error(e);
            }
        });
    }
}