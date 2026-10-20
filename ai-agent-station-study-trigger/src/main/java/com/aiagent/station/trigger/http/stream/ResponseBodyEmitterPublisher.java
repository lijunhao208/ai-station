package com.aiagent.station.trigger.http.stream;

import com.aiagent.station.domain.agent.adapter.port.AgentStreamPublisher;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.servlet.mvc.method.annotation.ResponseBodyEmitter;

import java.util.concurrent.atomic.AtomicBoolean;

/**
 * 将 {@link ResponseBodyEmitter} 适配为领域端口 {@link AgentStreamPublisher}。
 */
@Slf4j
public class ResponseBodyEmitterPublisher implements AgentStreamPublisher {

    private final ResponseBodyEmitter emitter;
    private final AtomicBoolean finished = new AtomicBoolean(false);

    public ResponseBodyEmitterPublisher(ResponseBodyEmitter emitter) {
        this.emitter = emitter;
    }

    @Override
    public void send(String data) {
        if (finished.get()) {
            return;
        }
        try {
            emitter.send(data);
        } catch (Exception e) {
            log.error("SSE 发送失败: {}", e.getMessage(), e);
        }
    }

    @Override
    public void complete() {
        if (!finished.compareAndSet(false, true)) {
            return;
        }
        try {
            emitter.complete();
        } catch (Exception e) {
            log.error("SSE complete 失败: {}", e.getMessage(), e);
        }
    }

    @Override
    public void fail(Throwable error) {
        if (!finished.compareAndSet(false, true)) {
            return;
        }
        try {
            emitter.completeWithError(error);
        } catch (Exception e) {
            log.error("SSE fail 失败: {}", e.getMessage(), e);
            try {
                emitter.complete();
            } catch (Exception ignored) {
                // ignore
            }
        }
    }
}
