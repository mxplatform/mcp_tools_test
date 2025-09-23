# Dockerfile for MCP server
FROM python:3.11-slim
WORKDIR /app
COPY app/ /app/
# Add MCP SDK install here later
CMD ["python", "-m", "app"]
