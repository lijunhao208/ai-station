-- Optional migration for databases created before agent_id type fix.
-- Converts ai_agent_task_schedule.agent_id from bigint to varchar(64)
-- to align with ai_agent.agent_id / Java PO (String).
--
-- Review data first: values should be business agent_id (e.g. '3'), not auto-increment pk.

ALTER TABLE `ai_agent_task_schedule`
  MODIFY COLUMN `agent_id` varchar(64) NOT NULL COMMENT '智能体业务ID（对应 ai_agent.agent_id）';
