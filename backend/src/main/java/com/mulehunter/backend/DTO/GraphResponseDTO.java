package com.mulehunter.backend.DTO;

import java.util.List;

public record GraphResponseDTO(
        List<GraphNodeDTO> nodes,
        List<GraphLinkDTO> links
) {}
