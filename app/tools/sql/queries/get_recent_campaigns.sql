SELECT
    campaign_name,
    MAX(campaign_id) as campaign_id,
    MAX(date) as latest_date
FROM event
WHERE account_id = :account_id
    AND domain = 'event.campaignactivity'
    AND platform = 'msg:na'
    AND event IN ('message_send', 'message_click', 'message_open', 'message_soft_bounce', 'message_hard_bounce', 'message_unsubscribe')
GROUP BY campaign_name
ORDER BY latest_date DESC
LIMIT :num_campaigns
