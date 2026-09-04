# AI Agent Station Study - Python 版

基于 **FastAPI + LangChain** 重写的 AI Agent 学习平台，与原 Java/Spring AI 版 API 兼容，可共用 MySQL 数据库与前端页面。

## 技术栈

| 组件 | 技术 |
|------|------|
| Web 框架 | FastAPI + Uvicorn |
| AI 框架 | LangChain + langchain-openai |
| 数据库 | MySQL + SQLAlchemy |
| 流式响应 | SSE (Server-Sent Events) |
| Agent 策略 | Auto / Flow / Fixed 三种 |

## 项目结构

```
ai-agent-station-python/
├── app/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置
│   ├── models/              # ORM 与 VO
│   ├── repository/          # 数据访问
│   ├── routers/             # HTTP 路由
│   └── services/
│       ├── armory/          # Agent 动态装配
│       └── execute/         # 三种执行策略
├── requirements.txt
├── .env.example
└── run.py
```

## 快速开始

### 1. 环境准备

- Python 3.11+
- MySQL（导入 `docs/dev-ops/mysql/sql/ai-agent-station-study.sql`）

### 2. 安装依赖

```bash
cd ai-agent-station-python
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填写 MySQL 和 OpenAI API 配置
```

### 4. 启动服务

```bash
python run.py
```

服务默认运行在 `http://localhost:8099`

### 5. 前端对接

修改前端 `js/api-service.js` 中的 `baseUrl`：

```javascript
baseUrl: 'http://localhost:8099/api/v1/agent'
```

然后启动静态页面：

```bash
cd docs/tag-v1.0/nginx/html
python -m http.server 8080
```

访问 `http://localhost:8080/index.html`

## API 接口

与 Java 版完全兼容：

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/agent/auto_agent` | SSE 流式对话 |
| GET | `/api/v1/agent/query_available_agents` | 查询可用 Agent |
| POST | `/api/v1/agent/armory_agent` | 装配指定 Agent |
| POST | `/api/v1/agent/armory_api` | 装配 API 配置 |

## 与 Java 版对比

| 功能 | Java 版 | Python 版 |
|------|---------|-----------|
| Auto Agent 四阶段 | ✅ | ✅ |
| Flow Agent | ✅ | ✅ |
| Fixed Agent | ✅ | ✅ |
| SSE 流式输出 | ✅ | ✅ |
| MySQL 配置驱动 | ✅ | ✅ |
| 动态 Armory 装配 | ✅ | ✅ |
| MCP 工具调用 | ✅ | 🔜 待完善 |
| RAG / pgvector | ✅ | 🔜 待完善 |
| Admin CRUD API | ✅ | 🔜 待完善 |
| 定时任务 | ✅ | 🔜 待完善 |

## 开发说明

- 数据库表结构与原 Java 项目共用，无需迁移
- Agent 配置通过 MySQL `ai_agent`、`ai_agent_flow_config`、`ai_client_config` 等表管理
- 启动时若 `AUTO_ARMORY_ENABLED=true`，会自动装配所有启用的 Agent
