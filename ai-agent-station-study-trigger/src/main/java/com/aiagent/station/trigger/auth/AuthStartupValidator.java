package com.aiagent.station.trigger.auth;

import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

import java.util.Arrays;
import java.util.List;

/**
 * 生产环境鉴权配置启动校验，避免弱 JWT / 关闭鉴权 / 过宽 CORS 上线。
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class AuthStartupValidator {

    private static final String WEAK_JWT_MARKER = "change-me";
    private static final int MIN_PROD_JWT_SECRET_LENGTH = 32;

    private final AuthProperties authProperties;

    @Value("${spring.profiles.active:}")
    private String activeProfiles;

    @PostConstruct
    public void validate() {
        boolean prod = Arrays.stream(activeProfiles.split(","))
                .map(String::trim)
                .anyMatch(p -> p.equalsIgnoreCase("prod"));
        if (!prod) {
            if (authProperties.isEnabled()
                    && StringUtils.hasText(authProperties.getJwtSecret())
                    && authProperties.getJwtSecret().contains(WEAK_JWT_MARKER)) {
                log.warn("当前 JWT 使用开发默认密钥，仅限本地；生产请设置 APP_AUTH_JWT_SECRET");
            }
            return;
        }

        if (!authProperties.isEnabled()) {
            throw new IllegalStateException("生产环境禁止关闭鉴权：app.auth.enabled 必须为 true");
        }

        String secret = authProperties.getJwtSecret();
        if (!StringUtils.hasText(secret)
                || secret.contains(WEAK_JWT_MARKER)
                || secret.length() < MIN_PROD_JWT_SECRET_LENGTH) {
            throw new IllegalStateException(
                    "生产环境 JWT 密钥无效：请通过 APP_AUTH_JWT_SECRET 注入至少 "
                            + MIN_PROD_JWT_SECRET_LENGTH + " 位的强随机密钥");
        }

        List<String> origins = authProperties.getCorsAllowedOrigins();
        if (origins != null && origins.stream().anyMatch("*"::equals)) {
            throw new IllegalStateException("生产环境禁止 CORS 使用 *，请配置 APP_AUTH_CORS_ORIGINS");
        }
    }
}
