package com.aiagent.station.trigger.auth;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

@Data
@Component
@ConfigurationProperties(prefix = "app.auth")
public class AuthProperties {

    /**
     * 是否启用 API 鉴权（管理端 + Agent 接口；关闭仅用于本地紧急排障）
     */
    private boolean enabled = true;

    /**
     * JWT 签名密钥，生产环境务必通过环境变量注入
     */
    private String jwtSecret = "change-me-ai-agent-station-jwt-secret";

    /**
     * Token 有效期（小时）
     */
    private long tokenExpireHours = 24;

    /**
     * 允许的 CORS 来源；为空或包含 * 时表示开发模式放宽
     */
    private List<String> corsAllowedOrigins = new ArrayList<>(List.of("http://localhost:8080", "http://127.0.0.1:8080"));

    /**
     * 无需鉴权的路径（Ant 风格）
     */
    private List<String> permitPaths = new ArrayList<>(List.of(
            "/api/v1/admin/admin-user/login",
            "/api/v1/admin/admin-user/validate-login"
    ));
}
