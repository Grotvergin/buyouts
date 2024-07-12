CREATE OR REPLACE VIEW upcoming_buyouts AS
SELECT b.pick_point,
       b.user_id,
       b.date_plan,
       b.date_fact,
       b.date_delivery,
       b.date_pick_up,
       b.feedback,
       p.good_link,
       p.type,
       p.request,
       b.id
FROM buyouts AS b
JOIN plans AS p ON p.id = b.plan
WHERE CURRENT_TIMESTAMP AT TIME ZONE 'MSK' <= date_plan + INTERVAL '1 hour' AND CURRENT_TIMESTAMP AT TIME ZONE 'MSK' >= date_plan - INTERVAL '1 hour'
  AND user_id IS NULL;