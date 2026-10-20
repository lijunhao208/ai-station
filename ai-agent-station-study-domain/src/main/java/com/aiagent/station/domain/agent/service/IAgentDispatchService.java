package com.aiagent.station.domain.agent.service;

import com.aiagent.station.domain.agent.adapter.port.AgentStreamPublisher;
import com.aiagent.station.domain.agent.model.entity.ExecuteCommandEntity;

/**
 * Agent 策略调度器接口
 */
public interface IAgentDispatchService {

    void dispatch(ExecuteCommandEntity requestParameter, AgentStreamPublisher publisher) throws Exception;

}
