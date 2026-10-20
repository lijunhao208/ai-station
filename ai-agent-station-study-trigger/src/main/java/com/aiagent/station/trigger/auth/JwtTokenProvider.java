package com.aiagent.station.trigger.auth;

import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.exceptions.JWTVerificationException;
import com.auth0.jwt.interfaces.DecodedJWT;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Date;

@Component
public class JwtTokenProvider {

    private final AuthProperties authProperties;

    public JwtTokenProvider(AuthProperties authProperties) {
        this.authProperties = authProperties;
    }

    public String createToken(String userId, String username) {
        Instant now = Instant.now();
        Instant expireAt = now.plus(authProperties.getTokenExpireHours(), ChronoUnit.HOURS);
        return JWT.create()
                .withIssuer("ai-agent-station")
                .withSubject(userId)
                .withClaim("username", username)
                .withIssuedAt(Date.from(now))
                .withExpiresAt(Date.from(expireAt))
                .sign(algorithm());
    }

    public DecodedJWT verify(String token) throws JWTVerificationException {
        return JWT.require(algorithm())
                .withIssuer("ai-agent-station")
                .build()
                .verify(token);
    }

    public String resolveBearerToken(String authorizationHeader) {
        if (!StringUtils.hasText(authorizationHeader)) {
            return null;
        }
        String header = authorizationHeader.trim();
        if (header.regionMatches(true, 0, "Bearer ", 0, 7)) {
            return header.substring(7).trim();
        }
        return null;
    }

    private Algorithm algorithm() {
        byte[] secret = authProperties.getJwtSecret().getBytes(StandardCharsets.UTF_8);
        return Algorithm.HMAC256(secret);
    }
}
