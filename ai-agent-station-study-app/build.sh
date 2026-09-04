# 普通镜像构建，随系统版本构建 amd/arm
docker build --load -t example/ai-agent-station-study-app:1.1 -f ./Dockerfile .

# 兼容 amd、arm 构建镜像
# docker buildx build --l oad --platform liunx/amd64,linux/arm64 -t developer/ai-agent-station-app:1.0 -f ./Dockerfile . --push