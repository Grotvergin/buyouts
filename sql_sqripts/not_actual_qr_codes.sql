CREATE OR REPLACE VIEW not_actual_qr_codes AS
SELECT DISTINCT u.id, u.name, u.qr_date
FROM users AS u
JOIN buyouts AS b ON u.id = b.user_id
WHERE u.qr_date!= CURRENT_DATE
AND b.date_delivery IS NOT NULL
AND b.date_pick_up IS NULL;