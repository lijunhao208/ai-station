-- AI Agent Station MySQL seed (sanitized, no real secrets)
-- Prerequisites: run 01-schema.sql first
--
-- Default admin: username=admin / password=admin123 (BCrypt)
-- Replace YOUR_API_KEY / base_url before calling LLM APIs.
--
-- This seed provides a minimal Auto Agent (agent_id=3) so
-- POST /api/v1/agent/auto_agent works after login + armory.

USE `ai-agent-station-study`;

SET NAMES utf8mb4;

-- ---------------------------------------------------------------------------
-- Admin (BCrypt for admin123)
-- ---------------------------------------------------------------------------
INSERT INTO `admin_user` (`id`, `user_id`, `username`, `password`, `status`, `create_time`, `update_time`)
VALUES
  (1, '10001', 'admin', '$2a$10$MLd7Hd5i3PjMO5LMX9hXY.hkj4NxxjzXnSgUWskM1QfscZftERL/e', 1, NOW(), NOW());

-- ---------------------------------------------------------------------------
-- OpenAI-compatible API (placeholder key)
-- ---------------------------------------------------------------------------
INSERT INTO `ai_client_api` (`id`, `api_id`, `base_url`, `api_key`, `completions_path`, `embeddings_path`, `status`, `create_time`, `update_time`)
VALUES
  (1, '1001', 'https://api.openai.com', 'YOUR_API_KEY', 'v1/chat/completions', 'v1/embeddings', 1, NOW(), NOW());

-- ---------------------------------------------------------------------------
-- Chat model used by Auto Agent clients
-- ---------------------------------------------------------------------------
INSERT INTO `ai_client_model` (`id`, `model_id`, `api_id`, `model_usage`, `model_name`, `model_type`, `status`, `create_time`, `update_time`)
VALUES
  (1, '3001', '1001', '3001-gpt-4o-mini', 'gpt-4o-mini', 'openai', 1, NOW(), NOW());

-- ---------------------------------------------------------------------------
-- Advisor (chat memory)
-- ---------------------------------------------------------------------------
INSERT INTO `ai_client_advisor` (`id`, `advisor_id`, `advisor_name`, `advisor_type`, `order_num`, `ext_param`, `status`, `create_time`, `update_time`)
VALUES
  (1, '4001', '对话记忆', 'ChatMemory', 1, '{\n    \"maxMessages\": 200\n}', 1, NOW(), NOW());

-- ---------------------------------------------------------------------------
-- System prompts for Auto Agent roles
-- ---------------------------------------------------------------------------
INSERT INTO `ai_client_system_prompt` (`id`, `prompt_id`, `prompt_name`, `prompt_content`, `description`, `status`, `create_time`, `update_time`)
VALUES
  (1, '6101', '6101-任务分析',
   '# 角色\n你是一个专业的任务分析师，名叫 AutoAgent Task Analyzer。\n# 核心职责\n你负责分析任务的当前状态、执行历史和下一步行动计划：\n1. **状态分析**: 深度分析当前任务完成情况和执行历史\n2. **进度评估**: 评估任务完成进度和质量\n3. **策略制定**: 制定下一步最优执行策略\n4. **完成判断**: 准确判断任务是否已完成\n# 输出格式\n**任务状态分析:**\n[当前任务完成情况的详细分析]\n**执行历史评估:**\n[对已完成工作的质量和效果评估]\n**下一步策略:**\n[具体的下一步执行计划和策略]\n**完成度评估:** [0-100]%\n**任务状态:** [CONTINUE/COMPLETED]',
   'Auto Agent 任务分析', 1, NOW(), NOW()),
  (2, '6102', '6102-任务执行',
   '# 角色\n你是一个精准任务执行器，名叫 AutoAgent Precision Executor。\n# 核心能力\n你专注于精准执行具体的任务步骤：\n1. **精准执行**: 严格按照分析师的策略执行任务\n2. **质量控制**: 确保每一步执行的准确性和完整性\n3. **结果记录**: 详细记录执行过程和结果\n# 输出格式\n**执行目标:**\n[本轮要执行的具体目标]\n**执行过程:**\n[详细的执行步骤]\n**执行结果:**\n[执行的具体结果]\n**质量检查:**\n[对执行结果的质量评估]',
   'Auto Agent 任务执行', 1, NOW(), NOW()),
  (3, '6103', '6103-质量监督',
   '# 角色\n你是一个专业的质量监督员，名叫 AutoAgent Quality Supervisor。\n# 核心职责\n你负责监督和评估执行质量：\n1. **质量评估**: 评估执行结果的准确性和完整性\n2. **问题识别**: 识别执行过程中的问题和不足\n3. **改进建议**: 提供具体的改进建议和优化方案\n# 输出格式\n**质量评估:**\n[对执行结果的详细质量评估]\n**问题识别:**\n[发现的问题和不足之处]\n**改进建议:**\n[具体的改进建议和优化方案]\n**质量评分:** [0-100]分\n**是否通过:** [PASS/FAIL/OPTIMIZE]',
   'Auto Agent 质量监督', 1, NOW(), NOW()),
  (4, '6104', '6104-响应助手',
   '# 角色\n你是一个智能响应助手，名叫 AutoAgent React。\n# 说明\n你负责对用户的即时问题进行快速响应和处理，适用于简单的查询和交互。\n今天是 {current_date}。',
   'Auto Agent 响应助手', 1, NOW(), NOW());

-- ---------------------------------------------------------------------------
-- Clients (Auto Agent pipeline)
-- ---------------------------------------------------------------------------
INSERT INTO `ai_client` (`id`, `client_id`, `client_name`, `description`, `status`, `create_time`, `update_time`)
VALUES
  (1, '3101', '3101-任务分析与状态判断', 'AutoAgent Task Analyzer', 1, NOW(), NOW()),
  (2, '3102', '3102-具体任务执行', 'AutoAgent Precision Executor', 1, NOW(), NOW()),
  (3, '3103', '3103-质量检查与优化', 'AutoAgent Quality Supervisor', 1, NOW(), NOW()),
  (4, '3104', '3104-智能响应助手', 'AutoAgent React', 1, NOW(), NOW());

-- ---------------------------------------------------------------------------
-- Client wiring: model / prompt / advisor (no MCP / no secrets)
-- ---------------------------------------------------------------------------
INSERT INTO `ai_client_config` (`id`, `source_type`, `source_id`, `target_type`, `target_id`, `ext_param`, `status`, `create_time`, `update_time`)
VALUES
  (1,  'client', '3101', 'model',   '3001', '""', 1, NOW(), NOW()),
  (2,  'client', '3101', 'prompt',  '6101', '""', 1, NOW(), NOW()),
  (3,  'client', '3101', 'advisor', '4001', '""', 1, NOW(), NOW()),
  (4,  'client', '3102', 'model',   '3001', '""', 1, NOW(), NOW()),
  (5,  'client', '3102', 'prompt',  '6102', '""', 1, NOW(), NOW()),
  (6,  'client', '3102', 'advisor', '4001', '""', 1, NOW(), NOW()),
  (7,  'client', '3103', 'model',   '3001', '""', 1, NOW(), NOW()),
  (8,  'client', '3103', 'prompt',  '6103', '""', 1, NOW(), NOW()),
  (9,  'client', '3103', 'advisor', '4001', '""', 1, NOW(), NOW()),
  (10, 'client', '3104', 'model',   '3001', '""', 1, NOW(), NOW()),
  (11, 'client', '3104', 'prompt',  '6104', '""', 1, NOW(), NOW()),
  (12, 'client', '3104', 'advisor', '4001', '""', 1, NOW(), NOW());

-- ---------------------------------------------------------------------------
-- Agent: Auto (matches README example aiAgentId=3)
-- ---------------------------------------------------------------------------
INSERT INTO `ai_agent` (`id`, `agent_id`, `agent_name`, `description`, `channel`, `strategy`, `status`, `create_time`, `update_time`)
VALUES
  (1, '3', '智能对话体（Auto）', '分析→执行→质检→总结 的自动多轮 Agent', 'agent', 'autoAgentExecuteStrategy', 1, NOW(), NOW());

-- ---------------------------------------------------------------------------
-- Auto Agent flow steps
-- ---------------------------------------------------------------------------
INSERT INTO `ai_agent_flow_config` (`id`, `agent_id`, `client_id`, `client_name`, `client_type`, `sequence`, `step_prompt`, `status`, `create_time`)
VALUES
  (1, '3', '3101', '任务分析和状态判断', 'TASK_ANALYZER_CLIENT', 1,
   '**原始用户需求:** %s\n**当前执行步骤:** 第 %d 步 (最大 %d 步)\n**历史执行记录:**\n%s\n**当前任务:** %s\n**分析要求:**\n请深入分析用户的具体需求，制定明确的执行策略：\n1. 理解用户真正想要什么\n2. 分析需要哪些具体的执行步骤\n3. 制定能够产生实际结果的执行策略\n4. 确保策略能够直接回答用户的问题\n**输出格式要求:**\n任务状态分析: [当前任务完成情况的详细分析]\n执行历史评估: [对已完成工作的质量和效果评估]\n下一步策略: [具体的执行计划]\n完成度评估: [0-100]%%\n任务状态: [CONTINUE/COMPLETED]',
   1, NOW()),
  (2, '3', '3102', '具体任务执行', 'PRECISION_EXECUTOR_CLIENT', 2,
   '**用户原始需求:** %s\n**分析师策略:** %s\n**执行指令:** 你是一个精准任务执行器，需要根据用户需求和分析师策略，实际执行具体的任务。\n**执行要求:**\n1. 直接执行用户的具体需求\n2. 提供具体的执行结果，而不只是描述过程\n3. 确保执行结果能直接回答用户的问题\n**输出格式:**\n执行目标: [明确的执行目标]\n执行过程: [实际执行的步骤]\n执行结果: [具体的执行成果]\n质量检查: [对执行结果的质量评估]',
   1, NOW()),
  (3, '3', '3103', '质量检查和优化', 'QUALITY_SUPERVISOR_CLIENT', 3,
   '**用户原始需求:** %s\n**执行结果:** %s\n**监督要求:**\n请严格评估执行结果是否真正满足了用户的原始需求：\n1. 检查是否直接回答了用户的问题\n2. 评估内容的完整性和实用性\n3. 判断是否只是描述过程而没有给出实际答案\n**输出格式:**\n需求匹配度: [匹配程度分析]\n内容完整性: [是否完整、具体、实用]\n问题识别: [发现的问题和不足]\n改进建议: [具体的改进建议]\n质量评分: [1-10分的质量评分]\n是否通过: [PASS/FAIL/OPTIMIZE]',
   1, NOW()),
  (4, '3', '3104', '智能响应助手', 'RESPONSE_ASSISTANT', 4,
   '基于以下执行过程，请直接回答用户的原始问题，提供最终的答案和结果：\n**用户原始问题:** %s\n**执行历史和过程:**\n%s\n**要求:**\n1. 直接回答用户的原始问题\n2. 基于执行过程中获得的信息和结果\n3. 提供具体、实用的最终答案\n4. 避免只描述执行过程，重点是最终答案\n请直接给出用户问题的最终答案：',
   1, NOW());

-- Optional empty placeholders (tables exist; no demo rows with secrets)
-- ai_client_tool_mcp / ai_client_rag_order / ai_agent_task_schedule / ai_agent_draw_config
-- can be configured later via admin APIs.
