package com.aiagent.station.domain.agent.service.execute.auto.support;

import java.util.Locale;
import java.util.regex.Pattern;

/**
 * 从模型自由文本中识别任务完成/质检结论，兼容常见中英文与格式变体。
 */
public final class AutoAgentCompletionJudge {

    private static final Pattern COMPLETED_STATUS = Pattern.compile(
            "(?i)(任务状态|task\\s*status)\\s*[:：]?\\s*COMPLETED\\b");

    private static final Pattern PROGRESS_100 = Pattern.compile(
            "(完成度评估|完成度|progress)\\s*[:：]?\\s*100\\s*%?");

    private static final Pattern PASS = Pattern.compile(
            "(?i)(是否通过|质检结果|supervision\\s*result)\\s*[:：]?\\s*(PASS|通过|YES)\\b");

    private static final Pattern FAIL = Pattern.compile(
            "(?i)(是否通过|质检结果|supervision\\s*result)\\s*[:：]?\\s*(FAIL|不通过|NO)\\b");

    private static final Pattern OPTIMIZE = Pattern.compile(
            "(?i)(是否通过|质检结果|supervision\\s*result)\\s*[:：]?\\s*(OPTIMIZE|优化)\\b");

    private AutoAgentCompletionJudge() {
    }

    public static boolean isTaskCompleted(String analysisResult) {
        if (analysisResult == null || analysisResult.isBlank()) {
            return false;
        }
        String text = analysisResult.trim();
        if (COMPLETED_STATUS.matcher(text).find()) {
            return true;
        }
        if (PROGRESS_100.matcher(text).find()) {
            return true;
        }
        // 兜底：整段明确写了 COMPLETED，且不像在列举历史状态
        String upper = text.toUpperCase(Locale.ROOT);
        return upper.contains("STATUS: COMPLETED") || upper.contains("STATUS：COMPLETED");
    }

    public enum SupervisionVerdict {
        PASS, FAIL, OPTIMIZE, UNKNOWN
    }

    public static SupervisionVerdict judgeSupervision(String supervisionResult) {
        if (supervisionResult == null || supervisionResult.isBlank()) {
            return SupervisionVerdict.UNKNOWN;
        }
        String text = supervisionResult.trim();
        if (FAIL.matcher(text).find() || text.contains("是否通过: FAIL") || text.contains("是否通过：FAIL")) {
            return SupervisionVerdict.FAIL;
        }
        if (OPTIMIZE.matcher(text).find() || text.contains("是否通过: OPTIMIZE") || text.contains("是否通过：OPTIMIZE")) {
            return SupervisionVerdict.OPTIMIZE;
        }
        if (PASS.matcher(text).find() || text.contains("是否通过: PASS") || text.contains("是否通过：PASS")
                || text.contains("是否通过: 通过") || text.contains("是否通过：通过")) {
            return SupervisionVerdict.PASS;
        }
        return SupervisionVerdict.UNKNOWN;
    }
}
