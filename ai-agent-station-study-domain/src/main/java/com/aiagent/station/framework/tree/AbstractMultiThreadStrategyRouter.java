package com.aiagent.station.framework.tree;

/**
 * Multi-thread strategy router stub (replaces external design-framework dependency).
 */
public abstract class AbstractMultiThreadStrategyRouter<T, D, R> implements StrategyHandler<T, D, R> {

    protected StrategyHandler<T, D, R> defaultStrategyHandler = (t, d) -> null;

    public abstract StrategyHandler<T, D, R> get(T requestParameter, D dynamicContext) throws Exception;

    protected abstract void multiThread(T requestParameter, D dynamicContext) throws Exception;

    protected abstract R doApply(T requestParameter, D dynamicContext) throws Exception;

    @Override
    public R apply(T requestParameter, D dynamicContext) throws Exception {
        multiThread(requestParameter, dynamicContext);
        return doApply(requestParameter, dynamicContext);
    }
}
