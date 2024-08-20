CREATE OR REPLACE VIEW forbidden_brands AS
SELECT customer_name
FROM plans AS p
JOIN buyouts AS b ON p.id = b.plan_id
WHERE b.fact_time < NOW() + INTERVAL '30 minutes'
GROUP BY customer_name;

CREATE OR REPLACE VIEW available AS
SELECT b.id, b.plan_time
FROM buyouts AS b
JOIN plans AS p ON p.id = b.plan_id
WHERE plan_time >= NOW()
AND plan_time <= NOW() + INTERVAL '12 hours'
AND user_id IS NULL
AND p.customer_name NOT IN (SELECT * FROM forbidden_brands)
ORDER BY 1
LIMIT 1;

CREATE OR REPLACE VIEW notif_order AS
SELECT user_id,
       plan_time,
       pick_point_id,
       feedback,
       good_id,
       request,
       buyouts.id
FROM buyouts
         JOIN plans ON buyouts.plan_id = plans.id
WHERE user_id IS NOT NULL
  AND fact_time IS NULL
  AND plan_time > NOW();

CREATE OR REPLACE VIEW notif_arrive AS
SELECT user_id,
       plan_time,
       pick_point_id,
       feedback,
       good_id,
       request,
       buyouts.id
FROM buyouts
         JOIN plans ON buyouts.plan_id = plans.id
WHERE user_id IS NOT NULL
  AND fact_time IS NOT NULL
  AND delivery_time IS NULL;

CREATE OR REPLACE VIEW users_without_active_buyouts AS
SELECT u.id AS user_id
FROM users u
LEFT JOIN buyouts b ON u.id = b.user_id AND b.fact_time IS NULL
WHERE b.id IS NULL
AND EXISTS (SELECT 1 FROM available)
ORDER BY u.id;

CREATE OR REPLACE VIEW users_with_old_qr AS
SELECT u.id AS user_id
FROM Users u
JOIN Buyouts b ON u.id = b.user_id
WHERE b.delivery_time IS NOT NULL
AND (u.qr_time < DATE_TRUNC('day', NOW()) OR u.qr_time IS NULL)
ORDER BY u.id;