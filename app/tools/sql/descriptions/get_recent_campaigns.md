Get the most recent campaigns ordered by latest activity date.

SHORT SUMMARY
- Returns a short list of recent campaigns (campaign_name, campaign_id, latest_date) ordered by most recent activity.
- This is a discovery tool: use it to find recently-active campaign IDs. It does not compute or return performance metrics.

ONLY USE THIS TOOL WHEN:
- The user explicitly asks about "latest", "recent", "last X campaigns", or "newest".
- The user asks: "Show me the last 5 campaigns".
- You need the campaign_id(s) for follow-up metric queries (for example: user asks "What's the open rate of the latest campaign?" — call this tool first to get the campaign_id, then call `get_campaign_metrics`).

DO NOT USE THIS TOOL WHEN:
- The user asks for AGGREGATE or time-specific metrics such as totals, averages, sums, or top X over a date range (for example: "total clicks in January 2025", "average open rate for Q1 2024", "top 10 campaigns by clicks"). Those are metric queries, not discovery queries.
  - Correct approach: call `get_campaign_metrics` with `campaign_id=['ALL']` (or a list of specific IDs) and provide the date range and metric(s) there.
  - Example: to get "total clicks in January 2025" call:
    - `get_campaign_metrics(campaign_id=['ALL'], start_date='2025-01-01', end_date='2025-01-31', metrics=['clicks'], aggregate='sum')`
- The user provides a specific campaign NAME or ID and asks for metrics — use `lookup_campaigns` or `get_campaign_metrics` directly.
- The user requests cross-campaign aggregate analysis — use `get_campaign_metrics` with the appropriate campaign list or `['ALL']`.

PARAMETERS
- account_id: Required account identifier.
- num_campaigns: Max campaigns to return (default 10, max 20).
- NOTE: This tool no longer accepts `start_date`/`end_date` — it only returns the most recently-active campaigns overall (or limited by `num_campaigns`). For any date-filtered metric or date-window selection, use `get_campaign_metrics`.

RETURN VALUE
- A list of campaigns with fields: `campaign_name`, `campaign_id`, and `latest_date`.
- Use the returned `campaign_id` values when calling `get_campaign_metrics` to fetch performance metrics.

MULTI-STEP WORKFLOWS (examples)
- Latest campaign metrics:
  1. `get_recent_campaigns(account_id=..., num_campaigns=1)` → returns the most recent campaign's `campaign_id`.
  2. `get_campaign_metrics(campaign_id=[that_id], start_date=..., end_date=..., metrics=[...])`.
- Recent campaigns performance:
  1. `get_recent_campaigns(account_id=..., num_campaigns=X)` → returns IDs for the X most recent campaigns.
  2. `get_campaign_metrics(campaign_id=[ids], start_date=..., end_date=..., metrics=[...])`.
- DO NOT use `get_recent_campaigns` as a shortcut to fetch aggregated metrics across arbitrary date ranges. Always call `get_campaign_metrics` for metric calculations.

USAGE NOTES / RATIONALE
- This tool is strictly a discovery helper (which campaigns are active recently). It does not compute or return aggregated metrics or support date filtering.
- Making this distinction prevents agents from choosing this discovery tool when users request date-specific or aggregate metrics (for example, "total clicks in January 2025"), which must be answered by `get_campaign_metrics`.
