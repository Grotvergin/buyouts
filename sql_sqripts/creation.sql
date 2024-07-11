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
    sex        CHAR(1) CHECK (sex IN ('M', 'F')) NOT NULL,
    name       VARCHAR(20),
    num_digits CHAR(4),
    city       VARCHAR(15) REFERENCES Cities (name),
    reg_date   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    video_link VARCHAR(100) CHECK (video_link LIKE 'https://drive.google.com/file/d/%'),
    qr_date    TIMESTAMP,
    qr_link    VARCHAR(100) CHECK (qr_link LIKE 'https://drive.google.com/file/d/%')
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
    good_link    VARCHAR(100) CHECK (good_link LIKE 'https://www.wildberries.ru/catalog/%') NOT NULL,
    quantity     NUMERIC(4) CHECK (quantity > 0)                                            NOT NULL,
    start_date   TIMESTAMP CHECK (start_date >= CURRENT_TIMESTAMP)                               NOT NULL,
    end_date     TIMESTAMP CHECK (end_date >= start_date)                                   NOT NULL,
    type         CHAR(6) CHECK (type IN ('return', 'save'))                                 NOT NULL,
    request      VARCHAR(50),
    customer_inn NUMERIC(10) REFERENCES customers (inn)                                     NOT NULL
);

CREATE TABLE Buyouts
(
    id              SERIAL PRIMARY KEY,
    pick_point      BIGINT REFERENCES Pick_Points (id),
    user_id         BIGINT REFERENCES Users (id),
    date_plan       TIMESTAMP,
    date_fact       TIMESTAMP CHECK (date_fact >= date_plan),
    date_delivery   TIMESTAMP CHECK (date_delivery >= date_fact),
    date_pick_up    TIMESTAMP CHECK (date_pick_up >= date_delivery),
    date_shipment   TIMESTAMP CHECK (date_shipment >= date_pick_up),
    photo_hist_link VARCHAR(100) CHECK (photo_hist_link LIKE 'https://drive.google.com/file/d/%'),
    photo_good_link VARCHAR(100) CHECK (photo_good_link LIKE 'https://drive.google.com/file/d/%'),
    feedback        VARCHAR(250),
    plan            BIGINT REFERENCES Plans (id) NOT NULL,
    price           NUMERIC(8, 2) CHECK (price > 0)
);

CREATE TABLE Payments
(
    timestamp TIMESTAMP,
    sum       NUMERIC(8, 2) CHECK (sum > 0),
    type      CHAR(8) CHECK (type IN ('buyout', 'feedback', 'fee')),
    buyout_id BIGINT REFERENCES Buyouts (id)
);