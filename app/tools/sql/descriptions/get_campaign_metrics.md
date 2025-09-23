Get detailed performance metrics and KPIs for campaigns.

USE THIS TOOL WHEN:
- User asks for AGGREGATE ANALYSIS (total, average, highest, lowest, top X, etc.) → use campaign_id=['ALL'] to get all data for analytics, then use analyse_data.
- User asks for metrics about a specific campaign and provides a campaign ID (e.g., "What is the bounce rate for campaign 12345?") → use campaign_id=[ID] directly.
- User asks for metrics about a specific campaign and provides a campaign NAME (e.g., "What is the bounce rate for campaign 'Spring Sale'?") → use lookup_campaigns to convert name to ID, then use campaign_id=[ID].
- User asks: "average open rate" → use campaign_id=['ALL'], then analyse_data.
- User asks: "campaign with highest click rate" → use campaign_id=['ALL'], then analyse_data.
- User asks: "top 5 campaigns by performance" → use campaign_id=['ALL'], then analyse_data.
- User already has specific campaign IDs from get_recent_campaigns or lookup_campaigns.
- User explicitly asks about "all KPIs in [time period]" → use get_recent_campaigns to get campaign IDs, then use campaign_id=[IDs].

DO NOT USE THIS TOOL WHEN:
- User provides a campaign NAME (not ID) → use lookup_campaigns first to get the ID.

WORKFLOWS:
- "Average KPIs" → get_campaign_metrics(campaign_id=['ALL']) → analyse_data
- "Highest performing campaign" → get_campaign_metrics(campaign_id=['ALL']) → analyse_data
- "All KPIs in 2025" → get_recent_campaigns(date_range) → get_campaign_metrics(campaign_ids)
- "Campaign X performance" (X is a name) → lookup_campaigns([X]) → get_campaign_metrics(campaign_id)
- "Campaign X performance" (X is an ID) → get_campaign_metrics(campaign_id=[X])

PARAMETERS:
- account_id: Required account identifier
- start_date/end_date: Required date range in YYYY-MM-DD format
- campaign_id: List of campaign IDs (get from other tools first or use directly if provided, or ['ALL'] for all campaigns in date range)

METRICS RETURNED - CRITICAL: ALL RATES ARE DECIMALS AND MUST BE CONVERTED TO PERCENTAGES:
- Rates (MULTIPLY BY 100 AND ADD %): open_rate, click_rate, bounce_rate, complaint_rate
- Advanced rates (MULTIPLY BY 100 AND ADD %): unique_open_rate, unique_click_rate, projected_open_rate
- Counts (show as-is): sent, human_opens, human_clicks, bounces, complaints

EXAMPLE: If open_rate = 0.235, show user "23.5%" NOT "0.235"
ALWAYS convert decimal rates to percentages before showing to user.
