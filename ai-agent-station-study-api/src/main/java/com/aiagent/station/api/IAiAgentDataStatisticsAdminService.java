package com.aiagent.station.api;

import com.aiagent.station.api.dto.DataStatisticsResponseDTO;
import com.aiagent.station.api.response.Response;

/**
 * 数据统计
 * 2025/10/4 10:33
 */
public interface IAiAgentDataStatisticsAdminService {

    /**
     * 获取系统数据统计
     * @return 统计数据响应
     */
    Response<DataStatisticsResponseDTO> getDataStatistics();
}
