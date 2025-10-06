Get aggregated performance metrics and KPIs.

USE THIS TOOL WHEN:
- User asks for AGGREGATE ANALYSIS or totals

DO NOT USE THIS TOOL WHEN:
- User provides a campaign NAME or ID.

WORKFLOWS:
- "All KPIs in 2025" → get_aggregate_recent_campaigns(date_range)

PARAMETERS:
- account_id: Required account identifier
- start_date/end_date: Required date range in YYYY-MM-DD format

METRICS RETURNED - CRITICAL: ALL RATES ARE DECIMALS AND MUST BE CONVERTED TO PERCENTAGES:
- Advanced rates (MULTIPLY BY 100 AND ADD %): unique_human_click_rate, projected_open_rate, bounce_rate
- Counts (show as-is): sent, delivered, total_bounces

EXAMPLE: If projected_open_rate = 0.235, show user "23.5%" NOT "0.235"
ALWAYS convert decimal rates to percentages before showing to user.
