package com.aiagent.station.trigger.auth;

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

/**
 * 管理员密码哈希：新密码一律 BCrypt；兼容历史明文并在登录成功后可升级。
 */
@Component
public class PasswordHasher {

    private final BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();

    public String encode(String rawPassword) {
        if (!StringUtils.hasText(rawPassword)) {
            return rawPassword;
        }
        if (isBcryptHash(rawPassword)) {
            return rawPassword;
        }
        return encoder.encode(rawPassword);
    }

    public boolean matches(String rawPassword, String storedPassword) {
        if (!StringUtils.hasText(rawPassword) || !StringUtils.hasText(storedPassword)) {
            return false;
        }
        if (isBcryptHash(storedPassword)) {
            return encoder.matches(rawPassword, storedPassword);
        }
        // 历史明文兼容
        return rawPassword.equals(storedPassword);
    }

    public boolean needsUpgrade(String storedPassword) {
        return StringUtils.hasText(storedPassword) && !isBcryptHash(storedPassword);
    }

    public boolean isBcryptHash(String value) {
        return value != null && (value.startsWith("$2a$") || value.startsWith("$2b$") || value.startsWith("$2y$"));
    }
}
