CREATE OR REPLACE VIEW prohibited_inn AS
SELECT u.id AS user_id, c.inn AS prohibited_inn FROM users AS u
JOIN buyouts AS b ON b.user_id = u.id AND b.date_fact BETWEEN (CURRENT_DATE - INTERVAL '2 weeks') AND CURRENT_DATE
JOIN plans AS p ON p.id = b.plan
JOIN customers AS c ON c.inn = p.customer_inn;