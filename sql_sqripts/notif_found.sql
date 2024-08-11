CREATE VIEW notif_found AS
SELECT user_id,
       plan_time,
       pick_point_id,
       feedback,
       good_link,
       request,
       buyouts.id
FROM buyouts
         JOIN plans ON buyouts.plan_id = plans.id
WHERE user_id IS NULL
  AND plan_time IS NOT NULL