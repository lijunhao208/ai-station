package com.aiagent.station.trigger.auth;

import org.springframework.context.annotation.Configuration;
import org.springframework.util.CollectionUtils;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.util.List;

@Configuration
public class WebMvcAuthConfig implements WebMvcConfigurer {

    private final AuthProperties authProperties;
    private final AdminAuthInterceptor adminAuthInterceptor;

    public WebMvcAuthConfig(AuthProperties authProperties, AdminAuthInterceptor adminAuthInterceptor) {
        this.authProperties = authProperties;
        this.adminAuthInterceptor = adminAuthInterceptor;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        // 管理端与 Agent 对话/装配接口统一 JWT 鉴权；登录等白名单见 app.auth.permit-paths
        var registration = registry.addInterceptor(adminAuthInterceptor)
                .addPathPatterns("/api/v1/admin/**")
                .addPathPatterns("/api/v1/agent/**");

        List<String> permitPaths = authProperties.getPermitPaths();
        if (!CollectionUtils.isEmpty(permitPaths)) {
            registration.excludePathPatterns(permitPaths.toArray(String[]::new));
        }
    }

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        List<String> origins = authProperties.getCorsAllowedOrigins();
        var cors = registry.addMapping("/api/**")
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                .allowedHeaders("*")
                .allowCredentials(true)
                .maxAge(3600);

        if (CollectionUtils.isEmpty(origins) || origins.stream().anyMatch("*"::equals)) {
            // 开发兜底：不带凭证的宽放行
            cors.allowedOriginPatterns("*").allowCredentials(false);
        } else {
            cors.allowedOrigins(origins.toArray(String[]::new));
        }
    }
}
