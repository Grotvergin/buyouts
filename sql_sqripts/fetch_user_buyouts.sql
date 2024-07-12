CREATE OR REPLACE FUNCTION fetch_buyouts_for_user(input_user_id INTEGER)
    RETURNS TABLE
            (
                pick_point    BIGINT,
                user_id       BIGINT,
                date_plan     TIMESTAMP,
                date_fact     TIMESTAMP,
                date_delivery TIMESTAMP,
                date_pick_up  TIMESTAMP,
                feedback      VARCHAR(250),
                good_link     VARCHAR(100),
                type          CHAR(6),
                request       VARCHAR(50),
                id            INTEGER
            )
AS
$$
BEGIN
    RETURN QUERY
        SELECT b.pick_point,
               b.user_id,
               b.date_plan,
               b.date_fact,
               b.date_delivery,
               b.date_pick_up,
               b.feedback,
               p.good_link,
               p.type,
               p.request,
               b.id
        FROM buyouts AS b
                 JOIN
             plans AS p
             ON
                 p.id = b.plan
        WHERE b.user_id = input_user_id;
END;
$$ LANGUAGE plpgsql;