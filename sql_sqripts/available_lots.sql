CREATE OR REPLACE VIEW available_lots AS
SELECT user_id, date_plan, feedback, p.good_link FROM upcoming_buyouts AS u
JOIN plans AS p ON p.id = u.plan
WHERE user_id NOT IN (SELECT user_id FROM prohibited_inn);