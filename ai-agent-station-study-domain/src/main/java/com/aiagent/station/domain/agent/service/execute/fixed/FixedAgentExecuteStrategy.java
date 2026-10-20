package com.aiagent.station.domain.agent.service.execute.fixed;

import com.aiagent.station.domain.agent.adapter.port.AgentStreamPublisher;
import com.aiagent.station.domain.agent.adapter.repository.IAgentRepository;
import com.aiagent.station.domain.agent.model.entity.AutoAgentExecuteResultEntity;
import com.aiagent.station.domain.agent.model.entity.ExecuteCommandEntity;
import com.aiagent.station.domain.agent.model.valobj.AiAgentClientFlowConfigVO;
import com.aiagent.station.domain.agent.model.valobj.enums.AiAgentEnumVO;
import com.aiagent.station.domain.agent.service.IExecuteStrategy;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.context.ApplicationContext;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;

/**
 * 固定执行策略
 */
@Slf4j
@Service("fixedAgentExecuteStrategy")
public class FixedAgentExecuteStrategy implements IExecuteStrategy {

    @Resource
    private IAgentRepository repository;

    @Resource
    protected ApplicationContext applicationContext;

    public static final String CHAT_MEMORY_CONVERSATION_ID_KEY = "chat_memory_conversation_id";
    public static final String CHAT_MEMORY_RETRIEVE_SIZE_KEY = "chat_memory_response_size";

    @Override
    public void execute(ExecuteCommandEntity requestParameter, AgentStreamPublisher publisher) throws Exception {
        List<AiAgentClientFlowConfigVO> aiAgentClientList = repository.queryAiAgentClientsByAgentId(requestParameter.getAiAgentId());

        String content = "";

        for (AiAgentClientFlowConfigVO config : aiAgentClientList) {
            ChatClient chatClient = getChatClientByClientId(config.getClientId());

            content = chatClient.prompt(requestParameter.getMessage() + "，" + content)
                    .system(s -> s.param("current_date", LocalDate.now().toString()))
                    .advisors(a -> a
                            .param(CHAT_MEMORY_CONVERSATION_ID_KEY, requestParameter.getSessionId())
                            .param(CHAT_MEMORY_RETRIEVE_SIZE_KEY, 100))
                    .call().content();

            log.info("智能体对话进行，客户端ID {}", requestParameter.getAiAgentId());
        }

        log.info("智能体对话请求，结果 {} {}", requestParameter.getAiAgentId(), content);

        if (content != null && !content.trim().isEmpty()) {
            publisher.sendJson(AutoAgentExecuteResultEntity.createSummaryResult(content, requestParameter.getSessionId()));
            log.info("✅ 已发送最终结果");
        }

        publisher.sendJson(AutoAgentExecuteResultEntity.createCompleteResult(requestParameter.getSessionId()));
        log.info("✅ 已发送完成标识");
    }

    private ChatClient getChatClientByClientId(String clientId) {
        return getBean(AiAgentEnumVO.AI_CLIENT.getBeanName(clientId));
    }

    @SuppressWarnings("unchecked")
    private <T> T getBean(String beanName) {
        return (T) applicationContext.getBean(beanName);
    }

}
