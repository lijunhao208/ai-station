package com.aiagent.station.domain.agent.service;

import com.aiagent.station.domain.agent.model.valobj.AiAgentVO;

import java.util.List;

/**
 * 装配接口
 * 2025/10/3 12:48
 */
public interface IArmoryService {

    List<AiAgentVO> acceptArmoryAllAvailableAgents();

    void acceptArmoryAgent(String agentId);

    List<AiAgentVO> queryAvailableAgents();

    void acceptArmoryAgentClientModelApi(String apiId);

}
