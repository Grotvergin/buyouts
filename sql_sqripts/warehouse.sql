CREATE OR REPLACE VIEW warehouse AS
SELECT b.date_pick_up, p.good_link, p.type, c.name, c.legal_name  FROM buyouts AS b
JOIN plans AS p ON p.id = b.plan
JOIN customers AS c ON c.inn = p.customer_inn
WHERE b.date_pick_up IS NOT NULL AND b.date_shipment IS NULL;