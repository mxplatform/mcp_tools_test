SELECT
  human_clicks,
  bot_clicks,
  unique_clicks,
  unique_bot_clicks,
  unique_human_clicks,
  sent,
  soft_bounces,
  hard_bounces,
  hard_bounces + soft_bounces AS total_bounces,
  unsubscribe,
  complaints,
  human_opens,
  bot_opens,
  unique_opens,
  unique_bot_opens,
  unique_human_opens,
  human_readers,
  bot_readers,
  pre_cached_opens_also_readers,
  sent - (hard_bounces + soft_bounces) AS "messages_delivered",
  (hard_bounces + soft_bounces) / sent AS "bounce_rate",
  sent - hard_bounces - soft_bounces - unique_bot_opens + pre_cached_opens_also_readers AS "projected_open_denominator",
  human_readers / nullIf(projected_open_denominator,0) AS "projected_unique_open_rate",
  unique_human_clicks / nullIf(sent - (hard_bounces + soft_bounces),0) AS "unique_human_click_rate",
  unsubscribe / nullIf(sent - (hard_bounces + soft_bounces), 0) AS "opt_out_rate"
FROM (
  SELECT
    sum(human_clicks) AS human_clicks,
    sum(bot_clicks) AS bot_clicks,
    sum(unique_clicks) AS unique_clicks,
    sum(unique_bot_clicks) AS unique_bot_clicks,
    sum(unique_human_clicks) AS unique_human_clicks,
    sum(sends) AS sent,
    sum(soft_bounces) AS soft_bounces,
    sum(hard_bounces) AS hard_bounces,
    sum(unsubscribe) AS unsubscribe,
    sum(complaints) AS complaints,
    sum(human_opens) AS human_opens,
    sum(bot_opens) AS bot_opens,
    sum(unique_opens) AS unique_opens,
    sum(unique_bot_opens) AS unique_bot_opens,
    sum(unique_human_opens) AS unique_human_opens,
    sum(human_readers) AS human_readers,
    sum(bot_readers) AS bot_readers,
    sum(pre_cached_opens_also_readers) AS pre_cached_opens_also_readers
  FROM (
    SELECT
      sumIf(count, event = 'message_send') AS sends,
      sumIf(count, event = 'message_click' AND NOT is_machine) AS human_clicks,
      sumIf(count, event = 'message_click' AND is_machine) AS bot_clicks,
      uniqMergeIf(member_state, event = 'message_click') AS unique_clicks,
      uniqMergeIf(member_state, event = 'message_click' AND is_machine) AS unique_bot_clicks,
      uniqMergeIf(member_state, event = 'message_click' AND NOT is_machine) AS unique_human_clicks,
      sumIf(count, event = 'message_soft_bounce') AS soft_bounces,
      sumIf(count, event = 'message_hard_bounce') AS hard_bounces,
      sumIf(count, event = 'message_unsubscribe') AS unsubscribe,
      sumIf(count, event = 'message_unsubscribe' AND event_reason = 'unsub-feedback-loop') AS complaints,
      sumIf(count, event = 'message_open' AND NOT is_machine) AS human_opens,
      sumIf(count, event = 'message_open' AND is_machine) AS bot_opens,
      uniqMergeIf(member_state, event = 'message_open') AS unique_opens,
      uniqMergeIf(member_state, event = 'message_open' AND is_machine) AS unique_bot_opens,
      uniqMergeIf(member_state, event = 'message_open' AND NOT is_machine) AS unique_human_opens,
      uniqMergeIf(member_state, (event = 'message_open' OR event = 'message_click') AND NOT is_machine) AS human_readers,
      uniqMergeIf(member_state, (event = 'message_open' OR event = 'message_click') AND is_machine) AS bot_readers,
      unique_bot_opens + human_readers - uniqMergeIf(
        member_state,
        event = 'message_open' OR (event = 'message_click' AND NOT is_machine)
      ) AS pre_cached_opens_also_readers
    FROM
      msg_totals_bysenddate_v
    WHERE
      domain = 'event.campaignactivity'
      AND channel = 'email'
      AND platform = 'msg:na'
      AND account_id = :account_id
      AND send_date >= :start_date
      AND send_date <= :end_date
	    GROUP BY
	      campaign_id
	    HAVING
	      sends > 0
	  )
  )
