package com.aiagent.station.trigger.job;

import com.aiagent.station.domain.agent.adapter.port.AgentStreamPublisher;
import com.aiagent.station.domain.agent.model.entity.ExecuteCommandEntity;
import com.aiagent.station.domain.agent.model.valobj.AiAgentTaskScheduleVO;
import com.aiagent.station.domain.agent.service.IAgentDispatchService;
import com.aiagent.station.domain.agent.service.ITaskService;
import com.aiagent.station.types.job.model.TaskScheduleVO;
import com.aiagent.station.types.job.provider.ITaskDataProvider;
import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.util.ArrayList;
import java.util.List;

/**
 * 智能体定时任务：从 taskParam 解析 message / maxStep 后调度执行。
 */
@Slf4j
@Service
public class AgentTaskJob implements ITaskDataProvider {

    private static final int DEFAULT_MAX_STEP = 3;

    @Resource
    private ITaskService taskService;

    @Resource
    private IAgentDispatchService dispatchService;

    @Override
    public List<TaskScheduleVO> queryAllValidTaskSchedule() {
        List<AiAgentTaskScheduleVO> aiAgentTaskScheduleVOS = taskService.queryAllValidTaskSchedule();
        List<TaskScheduleVO> result = new ArrayList<>();
        for (AiAgentTaskScheduleVO aiAgentTaskScheduleVO : aiAgentTaskScheduleVOS) {
            TaskScheduleVO taskScheduleVO = new TaskScheduleVO();
            taskScheduleVO.setId(aiAgentTaskScheduleVO.getId());
            taskScheduleVO.setDescription(aiAgentTaskScheduleVO.getDescription());
            taskScheduleVO.setCronExpression(aiAgentTaskScheduleVO.getCronExpression());
            taskScheduleVO.setTaskParam(aiAgentTaskScheduleVO.getTaskParam());
            taskScheduleVO.setTaskLogic(() -> {
                try {
                    ExecuteCommandEntity command = buildExecuteCommand(aiAgentTaskScheduleVO);
                    dispatchService.dispatch(command, AgentStreamPublisher.noop());
                } catch (Exception e) {
                    log.error("任务执行失败 id={} agentId={}", aiAgentTaskScheduleVO.getId(),
                            aiAgentTaskScheduleVO.getAgentId(), e);
                }
            });

            result.add(taskScheduleVO);
        }
        return result;
    }

    @Override
    public List<Long> queryAllInvalidTaskScheduleIds() {
        return taskService.queryAllInvalidTaskScheduleIds();
    }

    /**
     * 解析 taskParam：
     * <ul>
     *   <li>JSON：优先取 message / prompt / content，可选 maxStep</li>
     *   <li>非 JSON 纯文本：整段作为 message</li>
     * </ul>
     */
    ExecuteCommandEntity buildExecuteCommand(AiAgentTaskScheduleVO schedule) {
        if (!StringUtils.hasText(schedule.getAgentId())) {
            throw new IllegalArgumentException("定时任务缺少 agentId, taskId=" + schedule.getId());
        }

        String raw = schedule.getTaskParam();
        if (!StringUtils.hasText(raw)) {
            throw new IllegalArgumentException("定时任务 taskParam 为空, taskId=" + schedule.getId());
        }

        String message = null;
        int maxStep = DEFAULT_MAX_STEP;
        String trimmed = raw.trim();

        if (trimmed.startsWith("{")) {
            try {
                JSONObject obj = JSON.parseObject(trimmed);
                message = firstNonBlank(obj.getString("message"), obj.getString("prompt"), obj.getString("content"));
                Integer configuredMaxStep = obj.getInteger("maxStep");
                if (configuredMaxStep != null && configuredMaxStep > 0) {
                    maxStep = configuredMaxStep;
                }
            } catch (Exception e) {
                log.warn("taskParam JSON 解析失败，按纯文本处理 taskId={}: {}", schedule.getId(), e.getMessage());
                message = trimmed;
            }
        } else {
            message = trimmed;
        }

        if (!StringUtils.hasText(message)) {
            throw new IllegalArgumentException(
                    "定时任务 taskParam 未提供 message（可用 JSON.message 或纯文本）, taskId=" + schedule.getId());
        }

        return ExecuteCommandEntity.builder()
                .aiAgentId(schedule.getAgentId())
                .message(message)
                .sessionId("task_" + schedule.getId() + "_" + System.nanoTime())
                .maxStep(maxStep)
                .build();
    }

    private static String firstNonBlank(String... values) {
        if (values == null) {
            return null;
        }
        for (String value : values) {
            if (StringUtils.hasText(value)) {
                return value.trim();
            }
        }
        return null;
    }
}
