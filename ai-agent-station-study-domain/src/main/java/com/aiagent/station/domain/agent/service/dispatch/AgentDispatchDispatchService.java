package com.aiagent.station.domain.agent.service.dispatch;

import com.aiagent.station.domain.agent.adapter.port.AgentStreamPublisher;
import com.aiagent.station.domain.agent.adapter.repository.IAgentRepository;
import com.aiagent.station.domain.agent.model.entity.ExecuteCommandEntity;
import com.aiagent.station.domain.agent.model.valobj.AiAgentVO;
import com.aiagent.station.domain.agent.service.IAgentDispatchService;
import com.aiagent.station.domain.agent.service.IExecuteStrategy;
import com.aiagent.station.types.exception.BizException;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.concurrent.ThreadPoolExecutor;

/**
 * Agent 策略调度实现
 */
@Slf4j
@Service
public class AgentDispatchDispatchService implements IAgentDispatchService {

    @Resource
    private Map<String, IExecuteStrategy> executeStrategyMap;

    @Resource
    private IAgentRepository repository;

    @Resource
    private ThreadPoolExecutor threadPoolExecutor;

    @Override
    public void dispatch(ExecuteCommandEntity requestParameter, AgentStreamPublisher publisher) throws Exception {
        AiAgentVO aiAgentVO = repository.queryAiAgentByAgentId(requestParameter.getAiAgentId());
        if (aiAgentVO == null) {
            throw new BizException("智能体不存在 aiAgentId:" + requestParameter.getAiAgentId());
        }

        String strategy = aiAgentVO.getStrategy();
        IExecuteStrategy executeStrategy = executeStrategyMap.get(strategy);
        if (null == executeStrategy) {
            throw new BizException("不存在的执行策略类型 strategy:" + strategy);
        }

        threadPoolExecutor.execute(() -> {
            try {
                executeStrategy.execute(requestParameter, publisher);
            } catch (Exception e) {
                log.error("Agent 执行异常：{}", e.getMessage(), e);
                try {
                    publisher.send("执行异常：" + e.getMessage());
                } catch (Exception ex) {
                    log.error("发送异常信息失败：{}", ex.getMessage(), ex);
                }
                publisher.fail(e);
                return;
            }
            publisher.complete();
        });
    }

}
