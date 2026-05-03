
CREATE table dim_location (
    Location_id INT PRIMARY KEY,
    Borough VARCHAR(50),
    Zone_name VARCHAR(50),
    service_zone VARCHAR(50)
);

CREATE table dim_vendor (
    Vendor_id INT PRIMARY KEY,
    Vendor_name VARCHAR(255)
);

CREATE table dim_ratecode (
    RatecodeID INT PRIMARY KEY,
    Descriptions VARCHAR(255)
);

CREATE table dim_payment_type (
    payment_type INT PRIMARY KEY,
    Descriptions VARCHAR(255)
);

CREATE table dim_trip_type (
    trip_type INT PRIMARY KEY,
    Descriptions VARCHAR(255)
);

CREATE table dim_type (
    type_id INT PRIMARY KEY,
    Types VARCHAR(10)
);

CREATE table dim_date (
    date_id SERIAL PRIMARY KEY,
    year int,
    month int,
    day int
);

INSERT INTO dim_vendor (Vendor_id, Vendor_name) 
VALUES
(1, 'Creative Mobile Technologies, LLC'),
(2, 'VeriFone Inc.'),
(3, 'RideCharge Inc.'),
(4, 'Taxi Affiliation Services Inc.'),
(6, 'Myle Technologies Inc.'),
(7, 'Helix');

INSERT INTO dim_ratecode (RatecodeID, Descriptions) 
VALUES
(1, 'Standard rate'),
(2, 'JFK'),
(3, 'Newark'),
(4, 'Nassau or Westchester'),
(5, 'Negotiated fare'),
(6, 'Group ride'),
(99, 'Unknown');

INSERT INTO dim_payment_type (payment_type, Descriptions) 
VALUES
(0, 'Flex Fare trip'),
(1, 'Credit card'),
(2, 'Cash'),
(3, 'No charge'),
(4, 'Dispute'),
(5, 'Unknown'),
(6, 'Voided trip');

INSERT INTO dim_type (type_id, Types) 
VALUES
(1, 'yellow'),
(2, 'green');

INSERT INTO dim_trip_type (trip_type, Descriptions) 
VALUES
(0 , 'Unknown'),
(1, 'Street-hail'),
(2, 'Dispatch');


CREATE table trip_info (
    trip_id SERIAL PRIMARY KEY,
    trip_type int REFERENCES dim_trip_type(trip_type),
    type_id int REFERENCES dim_type(type_id),
    VendorID int REFERENCES dim_vendor(Vendor_id),
    passenger_count int ,
    trip_distance float,
    RatecodeID  int REFERENCES dim_ratecode(RatecodeID),
    PULocationID int REFERENCES dim_location(Location_id),
    DOLocationID int REFERENCES dim_location(Location_id)
);

CREATE table trip_data_payment (
    trip_id int PRIMARY KEY REFERENCES trip_info(trip_id),
    payment_type INT REFERENCES dim_payment_type(payment_type),
    fare_amount float,
    extra float,
    mta_tax float ,
    tip_amount float,
    tolls_amount float,
    improvement_surcharge float,
    total_amount float,
    congestion_surcharge int,
    Airport_fee float,
    cbd_congestion_fee float
);

CREATE table trip_data_time (
    trip_id int PRIMARY KEY REFERENCES trip_info(trip_id),
    pickup_date_id int REFERENCES dim_date(date_id),
    pickup_time time,
    duration time
);


