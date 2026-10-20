package com.aiagent.station.framework.tree;

/**
 * 策略树节点处理器。
 *
 * @param <T> 请求参数
 * @param <D> 动态上下文
 * @param <R> 返回结果
 */
public interface StrategyHandler<T, D, R> {

    StrategyHandler<?, ?, ?> DEFAULT = (t, d) -> null;

    @SuppressWarnings("unchecked")
    static <T, D, R> StrategyHandler<T, D, R> defaultHandler() {
        return (StrategyHandler<T, D, R>) DEFAULT;
    }

    R apply(T requestParameter, D dynamicContext) throws Exception;
}
