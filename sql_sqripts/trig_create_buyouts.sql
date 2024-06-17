CREATE OR REPLACE FUNCTION add_buyouts_from_plan()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.quantity IS NOT NULL THEN
        FOR i IN 1..NEW.quantity LOOP
            INSERT INTO buyouts (status, plan)
            VALUES ('created', NEW.id);
        END LOOP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_insert_into_plans
AFTER INSERT ON plans
FOR EACH ROW EXECUTE PROCEDURE add_buyouts_from_plan();