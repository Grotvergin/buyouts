CREATE OR REPLACE VIEW lost_during_delivery AS
SELECT b.pick_point, b.user_id, b.date_fact, b.photo_good_link, b.price, u.name FROM buyouts AS b
JOIN users AS u ON u.id = b.user_id
WHERE NOW() AT TIME ZONE 'MSK' > date_fact + INTERVAL '5 days' AND date_fact IS NOT NULL AND date_delivery IS NULL;

SELECT * FROM lost_during_delivery