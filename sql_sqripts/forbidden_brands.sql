CREATE VIEW forbidden_brands AS
SELECT customer_name
FROM plans AS p
JOIN buyouts AS b ON p.id = b.plan_id
WHERE b.fact_time < NOW() + INTERVAL '30 minutes'
GROUP BY customer_name