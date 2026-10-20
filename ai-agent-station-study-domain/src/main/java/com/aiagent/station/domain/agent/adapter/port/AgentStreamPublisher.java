package com.aiagent.station.domain.agent.adapter.port;

import com.alibaba.fastjson.JSON;

/**
 * Agent 执行过程的流式输出端口，隔离具体传输协议（如 HTTP SSE）。
 */
public interface AgentStreamPublisher {

    /**
     * 发送原始文本片段（调用方负责协议格式，如 SSE 的 data 行）。
     */
    void send(String data);

    /**
     * 发送 JSON 负载，封装为 SSE data 行。
     */
    default void sendJson(Object payload) {
        send("data: " + JSON.toJSONString(payload) + "\n\n");
    }

    /**
     * 正常结束流。
     */
    void complete();

    /**
     * 异常结束流。
     */
    void fail(Throwable error);

    /**
     * 丢弃输出（定时任务等无需回写客户端的场景）。
     */
    static AgentStreamPublisher noop() {
        return new AgentStreamPublisher() {
            @Override
            public void send(String data) {
                // ignore
            }

            @Override
            public void complete() {
                // ignore
            }

            @Override
            public void fail(Throwable error) {
                // ignore
            }
        };
    }
}
