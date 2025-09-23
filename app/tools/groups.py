from .registry import get_registry


def setup_tool_groups() -> None:
    """Setup predefined tool groups."""
    registry = get_registry()

    # Campaign tools
    registry.register_group("campaign_tools", ["get_recent_campaigns", "lookup_campaigns", "get_campaign_metrics"])

    # Analytics tools
    registry.register_group("analytics_tools", ["analyse_data"])

    # All SQL tools
    registry.register_group("sql_tools", ["get_recent_campaigns", "lookup_campaigns", "get_campaign_metrics"])
