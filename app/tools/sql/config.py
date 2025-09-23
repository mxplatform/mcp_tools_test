from dataclasses import dataclass
from typing import Dict, List, Optional

from ..schemas import CampaignLookupParams, CampaignRecentParams, KPIQueryArgs


@dataclass(frozen=True)
class SQLToolConfig:
    name: str
    args_schema: type
    output_schema: Optional[List[Dict[str, str]]] = None


CAMPAIGN_TOOL_CONFIGS: List[SQLToolConfig] = [
    SQLToolConfig("get_recent_campaigns", CampaignRecentParams, None),
    SQLToolConfig("lookup_campaigns", CampaignLookupParams, None),
    SQLToolConfig(
        "get_campaign_metrics",
        KPIQueryArgs,
        [
            {"column": "event", "type": "string"},
            {"column": "campaign_id", "type": "Int64"},
            {"column": "anyLast(campaign_name)", "type": "string"},
            {"column": "date", "type": "datetime64[ns]"},
            {"column": "human_clicks", "type": "Int64"},
            {"column": "bot_clicks", "type": "Int64"},
            {"column": "unique_clicks", "type": "Int64"},
            {"column": "unique_human_clicks", "type": "Int64"},
            {"column": "sent", "type": "Int64"},
            {"column": "total_sends", "type": "Int64"},
            {"column": "soft_bounces", "type": "Int64"},
            {"column": "hard_bounces", "type": "Int64"},
            {"column": "unsubscribe", "type": "Int64"},
            {"column": "total_opens", "type": "Int64"},
            {"column": "total_clicks", "type": "Int64"},
            {"column": "human_opens", "type": "Int64"},
            {"column": "bot_opens", "type": "Int64"},
            {"column": "unique_opens", "type": "Int64"},
            {"column": "unique_bot_opens", "type": "Int64"},
            {"column": "unique_human_opens", "type": "Int64"},
            {"column": "complaints", "type": "Int64"},
            {"column": "unique_pre_cached_opens", "type": "Int64"},
            {"column": "human_readers", "type": "Int64"},
            {"column": "pre_cached_openers_also_readers", "type": "Int64"},
            {"column": "complaint_rate", "type": "float64"},
            {"column": "open_rate", "type": "float64"},
            {"column": "unique_open_rate", "type": "float64"},
            {"column": "click_rate", "type": "float64"},
            {"column": "unique_click_rate", "type": "float64"},
            {"column": "bounce_rate", "type": "float64"},
            {"column": "projected_open_rate", "type": "float64"},
        ],
    ),
]

CONFIG_MAP: Dict[str, SQLToolConfig] = {c.name: c for c in CAMPAIGN_TOOL_CONFIGS}
