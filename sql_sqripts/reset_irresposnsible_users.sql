CREATE OR REPLACE FUNCTION reset_irresponsible_users()
    RETURNS VOID AS
$$
DECLARE
    row RECORD;
BEGIN
    FOR row IN SELECT id, user_id, date_fact, date_plan FROM Buyouts WHERE user_id IS NOT NULL AND date_fact IS NULL
        LOOP
            IF EXTRACT(EPOCH FROM (NOW() AT TIME ZONE 'MSK' - row.date_plan)) > 3600 THEN
                UPDATE Buyouts
                SET user_id = NULL, date_plan = NOW() AT TIME ZONE 'MSK' + INTERVAL '1 hour'
                WHERE id = row.id;
            END IF;
        END LOOP;
END;
$$ LANGUAGE plpgsql;