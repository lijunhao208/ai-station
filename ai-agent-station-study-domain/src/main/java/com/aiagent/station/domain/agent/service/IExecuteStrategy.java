package com.aiagent.station.domain.agent.service;

import com.aiagent.station.domain.agent.adapter.port.AgentStreamPublisher;
import com.aiagent.station.domain.agent.model.entity.ExecuteCommandEntity;

/**
 * 执行策略接口
 */
public interface IExecuteStrategy {

    void execute(ExecuteCommandEntity requestParameter, AgentStreamPublisher publisher) throws Exception;

}
