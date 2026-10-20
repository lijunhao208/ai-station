package com.aiagent.station.trigger.auth;

import com.aiagent.station.api.response.Response;
import com.aiagent.station.types.enums.ResponseCode;
import com.alibaba.fastjson.JSON;
import com.auth0.jwt.interfaces.DecodedJWT;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

import java.nio.charset.StandardCharsets;

@Slf4j
@Component
public class AdminAuthInterceptor implements HandlerInterceptor {

    public static final String ATTR_USER_ID = "auth.userId";
    public static final String ATTR_USERNAME = "auth.username";

    private final AuthProperties authProperties;
    private final JwtTokenProvider jwtTokenProvider;

    public AdminAuthInterceptor(AuthProperties authProperties, JwtTokenProvider jwtTokenProvider) {
        this.authProperties = authProperties;
        this.jwtTokenProvider = jwtTokenProvider;
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        if (!authProperties.isEnabled()) {
            return true;
        }
        if ("OPTIONS".equalsIgnoreCase(request.getMethod())) {
            return true;
        }

        String token = jwtTokenProvider.resolveBearerToken(request.getHeader("Authorization"));
        if (token == null || token.isBlank()) {
            writeUnauthorized(response, "缺少 Authorization Bearer Token");
            return false;
        }

        try {
            DecodedJWT jwt = jwtTokenProvider.verify(token);
            request.setAttribute(ATTR_USER_ID, jwt.getSubject());
            request.setAttribute(ATTR_USERNAME, jwt.getClaim("username").asString());
            return true;
        } catch (Exception e) {
            log.warn("Token 校验失败: {}", e.getMessage());
            writeUnauthorized(response, "Token 无效或已过期");
            return false;
        }
    }

    private void writeUnauthorized(HttpServletResponse response, String message) throws Exception {
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        response.setCharacterEncoding(StandardCharsets.UTF_8.name());
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        Response<Void> body = Response.<Void>builder()
                .code(ResponseCode.UNAUTHORIZED.getCode())
                .info(message)
                .data(null)
                .build();
        response.getWriter().write(JSON.toJSONString(body));
    }
}
