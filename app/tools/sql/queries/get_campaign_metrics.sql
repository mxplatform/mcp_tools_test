SELECT
    'kpi' AS event,
    *,
    complaints / nullIf(total_sends - hard_bounces - soft_bounces, 0) AS complaint_rate,
    total_opens / nullIf(total_sends - hard_bounces - soft_bounces, 0) AS open_rate,
    unique_human_opens / nullIf(sent, 0) AS unique_open_rate,
    human_clicks / nullIf(sent, 0) AS click_rate,
    unique_human_clicks / nullIf(sent, 0) AS unique_click_rate,
    (soft_bounces + hard_bounces) / nullIf(sent, 0) AS bounce_rate,
    human_readers / nullIf(total_sends - hard_bounces - soft_bounces - unique_pre_cached_opens + pre_cached_openers_also_readers, 0) AS projected_open_rate
FROM
(
    SELECT
        campaign_id,
        anyLast(campaign_name),
        anyLast(last_date) AS date,
        sumIf(count, (event = 'message_click') AND (NOT is_machine)) AS human_clicks,
        sumIf(count, (event = 'message_click') AND is_machine) AS bot_clicks,
        uniqMergeIf(member_state, (event = 'message_click') AND (is_machine IS NULL)) AS unique_clicks,
        uniqMergeIf(member_state, (event = 'message_click') AND (NOT is_machine)) AS unique_human_clicks,
        sumIf(count, (event = 'message_send') AND (is_machine IS NULL)) AS sent,
        sent AS total_sends,
        sumIf(count, (event = 'message_soft_bounce') AND (is_machine IS NULL)) AS soft_bounces,
        sumIf(count, (event = 'message_hard_bounce') AND (is_machine IS NULL)) AS hard_bounces,
        sumIf(count, (event = 'message_unsubscribe') AND (is_machine IS NULL)) AS unsubscribe,
        sumIf(count, (event = 'message_open') AND (is_machine IS NULL)) AS total_opens,
        sumIf(count, (event = 'message_click') AND (is_machine IS NULL)) AS total_clicks,
        sumIf(count, (event = 'message_open') AND (NOT is_machine)) AS human_opens,
        sumIf(count, (event = 'message_open') AND is_machine) AS bot_opens,
        uniqMergeIf(member_state,(event = 'message_open') AND (is_machine IS NULL)) AS unique_opens,
        uniqMergeIf(member_state, (event = 'message_open') AND is_machine) AS unique_bot_opens,
        uniqMergeIf(member_state, (event = 'message_open') AND (NOT is_machine)) AS unique_human_opens,
        sumIf(count, event = 'message_unsubscribe' AND event_reason = 'unsub-feedback-loop') AS complaints,
        uniqMergeIf(member_state, event = 'message_open' AND is_machine) AS unique_pre_cached_opens,
        uniqMergeIf(member_state, (event = 'message_open' OR event = 'message_click') AND NOT is_machine) AS human_readers,
        unique_pre_cached_opens + human_readers - uniqMergeIf(member_state, event = 'message_open' OR (event = 'message_click' AND NOT is_machine)) AS pre_cached_openers_also_readers
    FROM
    (
        SELECT
            event,
            event_reason,
            NULL AS is_machine,
            campaign_id,
            anyLast(campaign_name) AS campaign_name,
            sum(count) AS count,
            -- uniqMerge(member_state) AS members,
            max(send_date) AS last_date,
            uniqMergeState(member_state) as member_state
        FROM msg_totals_bysenddate
        WHERE
	        (domain = 'event.campaignactivity') AND
	        (platform = 'msg:na') AND
	        (account_id = :account_id) AND
	        (event IN ('message_send', 'message_click', 'message_open', 'message_soft_bounce', 'message_hard_bounce', 'message_unsubscribe')) AND
            (send_date BETWEEN :start_date AND :end_date) AND
        	((:campaign_id != ['ALL'] AND campaign_id IN :campaign_id) OR
        	(:campaign_id = ['ALL'] ))
        GROUP BY
            event,
            event_reason,
            is_machine,
            campaign_id
        UNION ALL
        SELECT
            event,
            event_reason,
            is_machine,
            campaign_id,
            anyLast(campaign_name) AS campaign_name,
            sum(count) AS count,
            -- uniqMerge(member_state) AS members,
            max(send_date) AS last_date,
            uniqMergeState(member_state) as member_state
        FROM msg_totals_bysenddate
        WHERE
        	(domain = 'event.campaignactivity') AND
        	(platform = 'msg:na') AND
        	(account_id = :account_id) AND
        	(event IN ('message_send', 'message_click', 'message_open', 'message_soft_bounce', 'message_hard_bounce', 'message_unsubscribe', 'message_unsubscribe')) AND
            (send_date BETWEEN :start_date AND :end_date) AND
        	((:campaign_id != ['ALL'] AND campaign_id IN :campaign_id) OR
        	(:campaign_id = ['ALL'] ))
        GROUP BY
            event,
            event_reason,
            is_machine,
            campaign_id
    )
    GROUP BY campaign_id
)
