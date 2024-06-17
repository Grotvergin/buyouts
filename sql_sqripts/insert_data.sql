INSERT INTO cities VALUES  ('Москва');
INSERT INTO users (id, sex, name, num_digits, city, video_link) VALUES
('8765456789', 'M', 'Виталик', 7898, 'Москва', 'https://www.youtube.com/watch?v=Fp26mMXE0tU&t=4958s');
INSERT INTO plans (good_link, quantity, start_date, end_date, type, request) VALUES
('https://www.wildberries.ru/catalog/61417283/detail.aspx', 20, '2024-06-04', '2024-06-30', 'return', 'Товары для дома');
INSERT INTO customers (inn, name, legal_name) VALUES
(1234567890, 'Костя злоебучий', 'ООО ВОДОР');
UPDATE buyouts SET date_plan = '2024-06-06 14:50' WHERE id = 1;
UPDATE buyouts SET date_plan = '2024-06-06 14:45' WHERE id = 2;
UPDATE buyouts SET user_id = 8765456789 WHERE id = 1;
UPDATE buyouts SET user_id = 342123 WHERE id = 2;
INSERT INTO users (id, sex, name, num_digits, city, qr_link, video_link) VALUES
(34213, 'M', 'Гена', 4947, 'Москва', 'link', 'video');
INSERT INTO users (id, sex, name, num_digits, city, qr_link, video_link) VALUES
(342123, 'M', 'ВАся', 4947, 'Москва', 'link', 'video');
