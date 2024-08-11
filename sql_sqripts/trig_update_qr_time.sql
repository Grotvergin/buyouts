CREATE OR REPLACE FUNCTION update_qr_time()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.qr_time IS NOT NULL THEN
        UPDATE users SET qr_time = NOW() WHERE id = NEW.id;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_qr_time
AFTER UPDATE ON users
FOR EACH ROW EXECUTE PROCEDURE update_qr_time();