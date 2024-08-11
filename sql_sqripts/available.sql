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