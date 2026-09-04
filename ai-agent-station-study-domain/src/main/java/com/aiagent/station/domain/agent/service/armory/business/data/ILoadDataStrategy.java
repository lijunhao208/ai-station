package com.aiagent.station.domain.agent.service.armory.business.data;

import com.aiagent.station.domain.agent.model.entity.ArmoryCommandEntity;
import com.aiagent.station.domain.agent.service.armory.node.factory.DefaultArmoryStrategyFactory;

/**
 * 数据加载策略
 *
 * 2025/6/27 17:16
 */
public interface ILoadDataStrategy {

    void loadData(ArmoryCommandEntity armoryCommandEntity, DefaultArmoryStrategyFactory.DynamicContext dynamicContext);

}
