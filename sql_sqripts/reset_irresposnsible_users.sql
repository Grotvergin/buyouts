CREATE OR REPLACE FUNCTION reset_irresponsible_users()
    RETURNS VOID AS
$$
DECLARE
    row RECORD;
BEGIN
    FOR row IN SELECT id, user_id, fact_time, plan_time
               FROM Buyouts
               WHERE user_id IS NOT NULL
                 AND fact_time IS NULL
        LOOP
            IF EXTRACT(EPOCH FROM (NOW() - row.plan_time)) > 3600 THEN
                UPDATE Buyouts
                SET user_id = NULL, plan_time = NOW() + INTERVAL '2 hours'
                WHERE id = row.id;
            END IF;
        END LOOP;
END;
$$ LANGUAGE plpgsql;