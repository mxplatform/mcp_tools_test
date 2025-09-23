import os


def build_clickhouse_uri() -> str:
    """
    Build a ClickHouse SQLAlchemy URI from environment variables.

    Reads the following environment variables:
        CLICKHOUSE_USER
        CLICKHOUSE_PASSWORD
        CLICKHOUSE_HOST
        CLICKHOUSE_PORT
        CLICKHOUSE_DATABASE

    Returns:
        str: ClickHouse connection URI, e.g.,
             clickhouse://<user>:<password>@<host>:<port>/<database>

    Raises:
        KeyError: If any required variable is missing.
    """
    keys = [
        "CLICKHOUSE_USER",
        "CLICKHOUSE_PASSWORD",
        "CLICKHOUSE_HOST",
        "CLICKHOUSE_PORT",
        "CLICKHOUSE_DATABASE",
    ]
    env = {}
    for key in keys:
        value = os.environ.get(key)
        if not value:
            raise KeyError(f"Missing required environment variable: {key}")
        env[key] = value

    return (
        f"clickhouse://{env['CLICKHOUSE_USER']}:{env['CLICKHOUSE_PASSWORD']}"
        f"@{env['CLICKHOUSE_HOST']}:{env['CLICKHOUSE_PORT']}/{env['CLICKHOUSE_DATABASE']}"
    )
