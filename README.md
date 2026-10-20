# AI Agent Station

AI Agent Station 是一个智能体编排平台，用来把模型、提示词、知识库和外部工具组合成可执行的 Agent，并按不同策略自动完成任务。

适合需要「配置好能力 → 自动跑流程 → 实时看到过程」的场景，而不是每次临时拼提示词或手工串工具。

## 能做什么

- **配置智能体**：为 Agent 绑定模型、系统提示词、顾问能力与外部工具，形成可复用的能力组合。
- **可视化编排**：通过画布连线描述流程，保存后即可按图执行，无需改业务代码。
- **多种执行方式**
  - 自动模式：分析需求 → 执行任务 → 质量检查 → 总结输出，可多轮迭代
  - 流程模式：先梳理可用工具，再规划步骤并逐步完成
  - 固定模式：按预设顺序串联多个对话能力
- **实时看过程**：对话过程中持续推送分析、执行、质检与总结阶段的结果，方便观察与调试。
- **接入外部工具**：统一接入已有工具能力（如检索、监控查询、消息通知等），由 Agent 在执行中按需调用。
- **知识增强**：可挂载知识库内容，让回答更贴合业务资料。
- **在线与定时**：支持在线对话执行，也支持按计划定时拉起指定 Agent 完成离线任务。
- **配置热更新**：调整模型、工具或提示词后可重新装配，后续请求使用新配置。

## 使用流程

1. 配置或在画布上编排 Agent（模型、提示词、工具、流程）
2. 保存并装配为可执行智能体
3. 发起对话或等待定时任务触发
4. 查看流式返回的思考过程与最终结果

## 对话接口示例

```http
POST /api/v1/agent/auto_agent
Authorization: Bearer <login 返回的 token>
Content-Type: application/json
```

```json
{
  "aiAgentId": "3",
  "message": "检索相关技术项目，列出一份学习计划",
  "sessionId": "session_1642345678901_abc123def",
  "maxStep": 5
}
```

返回为流式消息，常见阶段包括：分析、执行、监督、总结、完成。无 Token 或 Token 无效时返回 `401`。

## 配置说明

请勿将真实密钥、数据库密码等写入仓库。可参考：

- `ai-agent-station-study-app/src/main/resources/application-dev.yml.example`
- `ai-agent-station-python/.env.example`

将示例复制为本地配置后填写你自己的密钥与连接信息即可。

## API 鉴权

管理接口与 Agent 接口（含 `POST /api/v1/agent/auto_agent`）默认需要 JWT：

1. `POST /api/v1/admin/admin-user/login` 登录，响应 `data.token`
2. 后续请求携带头：`Authorization: Bearer <token>`
3. 流式对话请用支持自定义 Header 的客户端（如 `fetch`），不要用无法带 Header 的原生 `EventSource`
4. 新建/更新管理员密码会自动 BCrypt 哈希；历史明文密码在首次登录成功后会自动升级

配置项见 `app.auth.*`（JWT 密钥请用环境变量 `APP_AUTH_JWT_SECRET`）。本地临时关闭：`app.auth.enabled=false`。

## 快速开始

### 1. 初始化数据库

**MySQL（业务库）**

```bash
mysql -u root -p < docs/sql/mysql/01-schema.sql
mysql -u root -p ai-agent-station-study < docs/sql/mysql/02-seed.sql
```

- 库名默认：`ai-agent-station-study`
- Seed 默认管理员：`admin` / `admin123`（BCrypt）
- Seed 中 `ai_client_api.api_key` 为占位符 `YOUR_API_KEY`，请改成你自己的密钥（或通过管理端配置）

**PostgreSQL + pgvector（向量库）**

```bash
# 先创建库，例如：createdb -U postgres ai-rag-knowledge
psql -U postgres -d ai-rag-knowledge -f docs/sql/pgvector/init.sql
```

应用使用的向量表名为 `vector_store_openai`（见 `AiAgentConfig`）。

### 2. 配置并启动

1. 填写本地配置或环境变量（参考上方示例文件：`MYSQL_*`、`PG_*`、`OPENAI_*`、`APP_AUTH_JWT_SECRET`）
2. 启动应用服务
3. 登录拿 Token → 装配 Agent（如需要）→ 调用 `POST /api/v1/agent/auto_agent`（示例 `aiAgentId` 为 `"3"`）
