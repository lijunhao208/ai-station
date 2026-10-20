-- AI Agent Station PostgreSQL + pgvector init
-- Database name should match spring.datasource.pgvector.url (default: ai-rag-knowledge)
-- Usage (example):
--   docker run ... -e POSTGRES_DB=ai-rag-knowledge \
--     -v ./docs/sql/pgvector/init.sql:/docker-entrypoint-initdb.d/init.sql \
--     pgvector/pgvector:v0.5.0
-- Or manually:
--   psql -U postgres -d ai-rag-knowledge -f docs/sql/pgvector/init.sql

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Spring AI PgVectorStore default-style tables (UUID PK + JSONB metadata)

DROP TABLE IF EXISTS public.vector_store;
CREATE TABLE public.vector_store (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(1536)
);

DROP TABLE IF EXISTS public.store_openai;
CREATE TABLE public.store_openai (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(1536)
);

-- Used by AiAgentConfig.vectorStore (vectorTableName = vector_store_openai)
DROP TABLE IF EXISTS public.vector_store_openai;
CREATE TABLE public.vector_store_openai (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(1536)
);
