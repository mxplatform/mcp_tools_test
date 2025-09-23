Convert between campaign names and IDs.

USE THIS TOOL WHEN:
- User asks for metrics about a campaign and provides a campaign NAME (e.g., "What is the bounce rate for campaign 'Spring Sale'?") → use this tool to get the campaign ID, then use get_campaign_metrics.
- User asks: "How did Campaign X perform?" (X is a name) → use this tool to get the ID, then use get_campaign_metrics.
- User asks: "Compare Campaign A vs Campaign B performance" (names) → use this tool to get IDs, then use get_campaign_metrics.
- User mentions specific campaign names and you need their IDs for metrics.

DO NOT USE THIS TOOL WHEN:
- User provides a campaign ID (not a name) → use get_campaign_metrics directly.
- User asks about "all campaigns" or aggregated data → use get_campaign_metrics with campaign_id=['ALL'].
- User asks about recent/latest campaigns → use get_recent_campaigns first.

MULTI-STEP WORKFLOWS:
- Named campaign metrics: lookup_campaigns(campaign_names=['Campaign X']) → get_campaign_metrics(campaign_id=result)
- Multiple campaign comparison: lookup_campaigns(campaign_names=['A', 'B']) → get_campaign_metrics(campaign_id=results)

PARAMETERS:
- account_id: Required account identifier
- campaign_names: List of campaign names to get IDs for (optional)
- campaign_ids: List of campaign IDs to get names for (optional)

Provide either campaign_names OR campaign_ids, not both.
Returns exact matches: campaign_name and campaign_id pairs.
