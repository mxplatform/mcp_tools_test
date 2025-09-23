SELECT DISTINCT
    campaign_name,
    campaign_id
FROM event
WHERE account_id = :account_id
    AND domain = 'event.campaignactivity'
    AND platform = 'msg:na'
    AND event IN ('message_send', 'message_click', 'message_open', 'message_soft_bounce', 'message_hard_bounce', 'message_unsubscribe')
    AND (
        (:campaign_names IS NOT NULL AND campaign_name IN :campaign_names) OR
        (:campaign_ids IS NOT NULL AND campaign_id IN :campaign_ids)
    )
ORDER BY campaign_name
