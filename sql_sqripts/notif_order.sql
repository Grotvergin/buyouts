CREATE VIEW notif_order AS
SELECT user_id,
       plan_time,
       pick_point_id,
       feedback,
       good_link,
       request,
       buyouts.id
FROM buyouts
         JOIN plans ON buyouts.plan_id = plans.id
WHERE user_id IS NOT NULL
  AND fact_time IS NULL
  AND plan_time > NOW()