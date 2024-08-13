CREATE OR REPLACE FUNCTION update_qr_time()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.qr_link IS DISTINCT FROM OLD.qr_link THEN
        UPDATE users SET qr_time = NOW() WHERE id = NEW.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_qr_time
AFTER UPDATE ON users
FOR EACH ROW EXECUTE PROCEDURE update_qr_time();

CREATE OR REPLACE FUNCTION add_buyouts_from_plan()
RETURNS TRIGGER AS $$
DECLARE
    random_time TIMESTAMP;
    duration_seconds DOUBLE PRECISION;
BEGIN
    IF NEW.quantity IS NOT NULL THEN
        duration_seconds := EXTRACT(EPOCH FROM (NEW.end_time - NEW.start_time));
        FOR i IN 1..NEW.quantity LOOP
            random_time := NEW.start_time + (random() * duration_seconds) * INTERVAL '1 second';
            INSERT INTO buyouts (plan_id, plan_time) VALUES (NEW.id, random_time);
        END LOOP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_insert_into_plans
AFTER INSERT ON plans
FOR EACH ROW EXECUTE PROCEDURE add_buyouts_from_plan();