CREATE OR REPLACE VIEW not_picked_orders AS
SELECT u.qr_link,
       u.qr_date,
       p.city,
       p.street,
       p.house,
       p.building,
       pl.good_link,
       u.name,
       u.num_digits,
       b.date_delivery
FROM buyouts AS b
         JOIN pick_points AS p ON p.id = b.pick_point
         JOIN users AS u ON u.id = b.user_id
         JOIN plans AS pl ON pl.id = b.plan
WHERE b.date_delivery IS NOT NULL
  AND b.date_pick_up IS NULL;