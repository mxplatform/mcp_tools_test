
# mcp_tools_test

Proof-of-concept MCP server using the official Python SDK (`mcp[cli]`).

## Local Development

```sh
uv run python -m app.server
```

## Docker

Build and run the container:

```sh
docker-compose up --build
```

The server will be available at `localhost:8080`.

Use an MCP client configured for Streamable HTTP to connect and discover the tools and their descriptions (from `app/tools/descriptions/*.md`).
