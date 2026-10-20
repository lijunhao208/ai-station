package com.aiagent.station.domain.agent.service.execute.auto;

import com.aiagent.station.domain.agent.adapter.port.AgentStreamPublisher;
import com.aiagent.station.domain.agent.model.entity.AutoAgentExecuteResultEntity;
import com.aiagent.station.domain.agent.model.entity.ExecuteCommandEntity;
import com.aiagent.station.domain.agent.service.IExecuteStrategy;
import com.aiagent.station.domain.agent.service.execute.auto.step.factory.DefaultAutoAgentExecuteStrategyFactory;
import com.aiagent.station.framework.tree.StrategyHandler;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * 自动执行策略
 */
@Slf4j
@Service("autoAgentExecuteStrategy")
public class AutoAgentExecuteStrategy implements IExecuteStrategy {

    @Resource
    private DefaultAutoAgentExecuteStrategyFactory defaultAutoAgentExecuteStrategyFactory;

    @Override
    public void execute(ExecuteCommandEntity executeCommandEntity, AgentStreamPublisher publisher) throws Exception {
        StrategyHandler<ExecuteCommandEntity, DefaultAutoAgentExecuteStrategyFactory.DynamicContext, String> executeHandler
                = defaultAutoAgentExecuteStrategyFactory.armoryStrategyHandler();

        DefaultAutoAgentExecuteStrategyFactory.DynamicContext dynamicContext = new DefaultAutoAgentExecuteStrategyFactory.DynamicContext();
        dynamicContext.setMaxStep(executeCommandEntity.getMaxStep() != null ? executeCommandEntity.getMaxStep() : 3);
        dynamicContext.setExecutionHistory(new StringBuilder());
        dynamicContext.setCurrentTask(executeCommandEntity.getMessage());
        dynamicContext.setValue("emitter", publisher);

        String apply = executeHandler.apply(executeCommandEntity, dynamicContext);
        log.info("自动执行结果:{}", apply);

        try {
            publisher.sendJson(AutoAgentExecuteResultEntity.createCompleteResult(executeCommandEntity.getSessionId()));
        } catch (Exception e) {
            log.error("发送完成标识失败：{}", e.getMessage(), e);
        }
    }

}
