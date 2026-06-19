package com.mulehunter.backend.websocket;

import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Component;

@Component
public class FraudAlertPublisher {

    private final SimpMessagingTemplate messagingTemplate;

    public FraudAlertPublisher(SimpMessagingTemplate messagingTemplate) {
        this.messagingTemplate = messagingTemplate;
    }

    public void publish(FraudAlertEvent event) {
        messagingTemplate.convertAndSend(
                "/topic/fraud-alerts",
                event
        );
    }
}
