TRUNCATE TABLE users;
TRUNCATE TABLE buyouts;
TRUNCATE TABLE plans;

DROP TABLE IF EXISTS buyouts CASCADE;
DROP TABLE IF EXISTS plans CASCADE;
DROP TABLE IF EXISTS users CASCADE;

DROP VIEW IF EXISTS forbidden_brands;
DROP VIEW IF EXISTS available;
DROP VIEW IF EXISTS notif_order;
DROP VIEW IF EXISTS notif_arrive;
DROP VIEW IF EXISTS users_without_active_buyouts;
DROP VIEW IF EXISTS users_with_old_qr;

DROP TRIGGER IF EXISTS update_qr_time ON users;
DROP TRIGGER IF EXISTS after_insert_into_plans ON plans;

DROP FUNCTION IF EXISTS reset_irresponsible_users();
DROP FUNCTION IF EXISTS update_qr_time();
DROP FUNCTION IF EXISTS add_buyouts_from_plan();