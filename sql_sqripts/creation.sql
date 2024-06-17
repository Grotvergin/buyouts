CREATE TABLE Cities
(
    name VARCHAR(30) PRIMARY KEY
);

CREATE TABLE Streets
(
    name VARCHAR(40) PRIMARY KEY
);

DELETE FROM Users WHERE id = 386988582

CREATE TABLE Users
(
    id         NUMERIC(11) PRIMARY KEY,
    sex        CHAR(1) CHECK (sex IN ('M', 'F'))    NOT NULL,
    name       VARCHAR(30),
    num_digits NUMERIC(4),
    city       VARCHAR(15) REFERENCES Cities (name),
    qr_link    VARCHAR(100),
    reg_date   DATE DEFAULT CURRENT_DATE,
    video_link VARCHAR(100),
    qr_date    TIMESTAMP
);

CREATE TABLE Pick_Points
(
    id       SERIAL PRIMARY KEY,
    city     VARCHAR(20) REFERENCES Cities (name),
    street   VARCHAR(30) REFERENCES Streets (name),
    house    NUMERIC(3) NOT NULL CHECK (house > 0),
    building NUMERIC CHECK (building > 0)
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
    good_link    VARCHAR(100),
    quantity     NUMERIC(4) CHECK (quantity > 0)        NOT NULL,
    start_date   DATE,
    end_date     DATE CHECK (end_date > start_date),
    type         VARCHAR(10) CHECK (type IN ('return', 'save')),
    request      VARCHAR(50),
    customer_inn NUMERIC(10) REFERENCES customers (inn) NOT NULL
);

CREATE TABLE Buyouts
(
    id              SERIAL PRIMARY KEY,
    pick_point      BIGINT REFERENCES Pick_Points (id),
    user_id         BIGINT REFERENCES Users (id),
    date_plan       TIMESTAMP,
    date_fact       TIMESTAMP,
    date_pick_up    TIMESTAMP CHECK (date_pick_up > date_delivery),
    date_shipment   TIMESTAMP CHECK (date_shipment > date_pick_up),
    photo_hist_link VARCHAR(100),
    photo_good_link VARCHAR(100),
    date_delivery   TIMESTAMP CHECK (date_delivery > date_fact),
    feedback        VARCHAR(250),
    plan            BIGINT REFERENCES Plans (id),
    price           NUMERIC(8, 2) CHECK (price > 0)
);

CREATE TABLE Payments
(
    timestamp TIMESTAMP,
    sum       NUMERIC(8, 2) CHECK (sum > 0),
    type      VARCHAR(20) CHECK (type IN ('buyout', 'feedback', 'fee')),
    buyout_id BIGINT REFERENCES Buyouts (id)
);
