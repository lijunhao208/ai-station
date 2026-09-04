package com.aiagent.station.api;

import com.aiagent.station.api.dto.AiAgentResponseDTO;
import com.aiagent.station.api.dto.ArmoryAgentRequestDTO;
import com.aiagent.station.api.dto.ArmoryApiRequestDTO;
import com.aiagent.station.api.dto.AutoAgentRequestDTO;
import com.aiagent.station.api.response.Response;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.web.servlet.mvc.method.annotation.ResponseBodyEmitter;

import java.util.List;

/**
 * Ai Agent 服务接口
 *
 * 2025/8/7 17:52
 */
public interface IAiAgentService {

    ResponseBodyEmitter autoAgent(AutoAgentRequestDTO request, HttpServletResponse response);

    /**
     * 装配智能体
     */
    Response<Boolean> armoryAgent(ArmoryAgentRequestDTO request);

    /**
     * 查询可用的智能体列表
     */
    Response<List<AiAgentResponseDTO>> queryAvailableAgents();

    /**
     * 装配API
     */
    Response<Boolean> armoryApi(ArmoryApiRequestDTO request);

}
