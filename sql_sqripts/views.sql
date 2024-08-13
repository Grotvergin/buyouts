CREATE VIEW forbidden_brands AS
SELECT customer_name
FROM plans AS p
JOIN buyouts AS b ON p.id = b.plan_id
WHERE b.fact_time < NOW() + INTERVAL '30 minutes'
GROUP BY customer_name;

CREATE VIEW available AS
SELECT b.id, b.plan_time
FROM buyouts AS b
JOIN plans AS p ON p.id = b.plan_id
WHERE plan_time >= NOW()
AND plan_time <= NOW() + INTERVAL '12 hours'
AND user_id IS NULL
AND p.customer_name NOT IN (SELECT * FROM forbidden_brands)
ORDER BY 1
LIMIT 1;

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
  AND plan_time > NOW();

CREATE VIEW notif_arrive AS
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
  AND fact_time IS NOT NULL
  AND pick_up_time IS NULL;

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
  AND plan_time IS NOT NULL;