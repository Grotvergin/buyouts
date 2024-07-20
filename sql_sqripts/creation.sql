CREATE TABLE Cities
(
    name VARCHAR(30) PRIMARY KEY
);

CREATE TABLE Streets
(
    name VARCHAR(40) PRIMARY KEY
);

CREATE TABLE Users
(
    id         NUMERIC(11) PRIMARY KEY,
    sex        CHAR(1) CHECK (sex IN ('M', 'F')),
    name       VARCHAR(20),
    surname    VARCHAR(25),
    phone      NUMERIC(11),
    city       VARCHAR(15) REFERENCES Cities (name),
    conf_time  TIMESTAMP,
    video_link VARCHAR(40),
    qr_time    TIMESTAMP,
    qr_link    VARCHAR(40)
);

CREATE TABLE Pick_Points
(
    id       SERIAL PRIMARY KEY,
    city     VARCHAR(20) REFERENCES Cities (name),
    street   VARCHAR(30) REFERENCES Streets (name),
    house    NUMERIC(3) NOT NULL CHECK (house > 0),
    building NUMERIC(3) CHECK (building > 0)
);

CREATE TABLE Customers
(
    inn        NUMERIC(10) PRIMARY KEY,
    name       VARCHAR(70),
    legal_name VARCHAR(50)
);

CREATE TABLE Plans
(
    id           SERIAL PRIMARY KEY,
    good_link    NUMERIC(9),
    quantity     NUMERIC(4) CHECK (quantity > 0)          NOT NULL,
    start_time   TIMESTAMP CHECK (start_time >= NOW())    NOT NULL,
    end_time     TIMESTAMP CHECK (end_time >= start_time) NOT NULL,
    request      VARCHAR(50),
    customer_inn NUMERIC(10) REFERENCES customers (inn)   NOT NULL
);

CREATE TABLE Buyouts
(
    id              SERIAL PRIMARY KEY,
    pick_point_id   BIGINT REFERENCES Pick_Points (id),
    user_id         BIGINT REFERENCES Users (id),
    plan_time       TIMESTAMP,
    fact_time       TIMESTAMP CHECK (fact_time >= plan_time),
    delivery_time   TIMESTAMP CHECK (delivery_time >= fact_time),
    pick_up_time    TIMESTAMP CHECK (pick_up_time >= delivery_time),
    photo_hist_link VARCHAR(40),
    photo_good_link VARCHAR(40),
    feedback        VARCHAR(250),
    plan_id         BIGINT REFERENCES Plans (id) NOT NULL,
    price           NUMERIC(8, 2) CHECK (price > 0)
);