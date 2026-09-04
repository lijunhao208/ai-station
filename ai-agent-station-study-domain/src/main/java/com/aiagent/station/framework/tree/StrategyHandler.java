package com.aiagent.station.framework.tree;

/**
 * Strategy tree handler stub (replaces external design-framework dependency).
 */
public interface StrategyHandler<T, D, R> {
    R apply(T requestParameter, D dynamicContext) throws Exception;
}
