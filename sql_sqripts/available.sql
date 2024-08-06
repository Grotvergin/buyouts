CREATE VIEW available AS
SELECT id, plan_time
FROM buyouts
WHERE plan_time >= NOW()
  AND plan_time <= NOW() + INTERVAL '12 hours'
AND user_id IS NULL
ORDER BY 1
LIMIT 1;