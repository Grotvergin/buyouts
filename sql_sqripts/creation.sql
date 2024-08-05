CREATE TABLE Users
(
    id         NUMERIC(11) PRIMARY KEY,
    sex        CHAR(1) CHECK (sex IN ('M', 'F')),
    name       VARCHAR(20),
    surname    VARCHAR(25),
    phone      NUMERIC(11),
    conf_time  TIMESTAMP,
    video_link VARCHAR(40),
    qr_time    TIMESTAMP,
    qr_link    VARCHAR(40)
);

-- qr_time    TIMESTAMP CHECK (qr_time >= NOW() - INTERVAL '5 minutes')
-- conf_time  TIMESTAMP CHECK (conf_time >= NOW() - INTERVAL '5 minutes')

CREATE TABLE Plans
(
    id           SERIAL PRIMARY KEY,
    good_link    NUMERIC(9),
    quantity     NUMERIC(4) CHECK (quantity > 0)          NOT NULL,
    start_time   TIMESTAMP CHECK (start_time >= NOW())    NOT NULL,
    end_time     TIMESTAMP CHECK (end_time >= start_time) NOT NULL,
    request      VARCHAR(50),
    customer_name VARCHAR(40) NOT NULL
);

CREATE TABLE Buyouts
(
    id              SERIAL PRIMARY KEY,
    pick_point_id   BIGINT,
    user_id         BIGINT REFERENCES Users (id),
    plan_time       TIMESTAMP,
    fact_time       TIMESTAMP CHECK (fact_time >= (plan_time - INTERVAL '20 minutes')),
    delivery_time   TIMESTAMP CHECK (delivery_time > fact_time),
    pick_up_time    TIMESTAMP CHECK (pick_up_time > delivery_time),
    photo_hist_link VARCHAR(40),
    photo_good_link VARCHAR(40),
    feedback        VARCHAR(250),
    plan_id         BIGINT REFERENCES Plans (id) NOT NULL,
    price           NUMERIC(6) CHECK (price > 0)
);