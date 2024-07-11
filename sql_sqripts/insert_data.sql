INSERT INTO cities VALUES  ('Москва');
INSERT INTO customers (inn, name, legal_name) VALUES
(1234567890, 'Костя злоебучий', 'ООО ВОДОР');
INSERT INTO plans (good_link, quantity, start_date, end_date, type, request, customer_inn) VALUES
('https://www.wildberries.ru/catalog/61417283/detail.aspx', 20, '2024-07-12', '2024-07-20', 'return', 'Товары для дома', 1234567890);
UPDATE buyouts SET date_plan = '2024-07-12 08:00' WHERE id = 1;
UPDATE buyouts SET date_plan = '2024-07-12 10:00' WHERE id = 2;
