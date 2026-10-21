package com.aiagent.station.domain.agent.service.execute.auto.step;

import com.aiagent.station.domain.agent.adapter.port.AgentStreamPublisher;
import com.aiagent.station.domain.agent.adapter.repository.IAgentRepository;
import com.aiagent.station.domain.agent.model.entity.AutoAgentExecuteResultEntity;
import com.aiagent.station.domain.agent.model.entity.ExecuteCommandEntity;
import com.aiagent.station.domain.agent.model.valobj.AiAgentClientFlowConfigVO;
import com.aiagent.station.domain.agent.model.valobj.enums.AiAgentEnumVO;
import com.aiagent.station.domain.agent.service.execute.auto.step.factory.DefaultAutoAgentExecuteStrategyFactory;
import com.aiagent.station.framework.tree.AbstractMultiThreadStrategyRouter;
import com.aiagent.station.types.exception.BizException;
import jakarta.annotation.Resource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.context.ApplicationContext;

import java.util.Map;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeoutException;

/**
 * 2025/7/27 16:48
 */
public abstract class AbstractExecuteSupport extends AbstractMultiThreadStrategyRouter<ExecuteCommandEntity, DefaultAutoAgentExecuteStrategyFactory.DynamicContext, String> {

    private final Logger log = LoggerFactory.getLogger(AbstractExecuteSupport.class);

    @Resource
    protected ApplicationContext applicationContext;

    @Resource
    protected IAgentRepository repository;

    public static final String CHAT_MEMORY_CONVERSATION_ID_KEY = "chat_memory_conversation_id";
    public static final String CHAT_MEMORY_RETRIEVE_SIZE_KEY = "chat_memory_response_size";

    @Override
    protected void multiThread(ExecuteCommandEntity requestParameter, DefaultAutoAgentExecuteStrategyFactory.DynamicContext dynamicContext) throws ExecutionException, InterruptedException, TimeoutException {

    }

    protected ChatClient getChatClientByClientId(String clientId) {
        return getBean(AiAgentEnumVO.AI_CLIENT.getBeanName(clientId));
    }

    /**
     * 按 clientType 取流程配置；缺失时抛明确业务异常，避免 NPE。
     */
    protected AiAgentClientFlowConfigVO requireFlowConfig(
            DefaultAutoAgentExecuteStrategyFactory.DynamicContext dynamicContext,
            String clientType) {
        Map<String, AiAgentClientFlowConfigVO> map = dynamicContext.getAiAgentClientFlowConfigVOMap();
        AiAgentClientFlowConfigVO config = map == null ? null : map.get(clientType);
        if (config == null) {
            throw new BizException("0002", "缺少 Auto Agent 流程配置 clientType=" + clientType);
        }
        return config;
    }

    protected <T> T getBean(String beanName) {
        return (T) applicationContext.getBean(beanName);
    }

    /**
     * 通用的SSE结果发送方法
     * @param dynamicContext 动态上下文
     * @param result 要发送的结果实体
     */
    protected void sendSseResult(DefaultAutoAgentExecuteStrategyFactory.DynamicContext dynamicContext,
                                 AutoAgentExecuteResultEntity result) {
        try {
            AgentStreamPublisher publisher = dynamicContext.getValue("emitter");
            if (publisher != null) {
                publisher.sendJson(result);
            }
        } catch (Exception e) {
            log.error("发送SSE结果失败：{}", e.getMessage(), e);
        }
    }

}
