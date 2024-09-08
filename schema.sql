
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS tradesmen;
DROP TABLE IF EXISTS jobs;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    postcode TEXT NOT NULL,
    hash TEXT NOT NULL
);

CREATE TABLE groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    postcode TEXT NOT NULL
);

CREATE TABLE tradesmen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade TEXT NOT NULL,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    postcode TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    call_out_fee INTEGER,
    hourly_rate INTEGER
);

CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tradesman_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    call_out_fee INTEGER,
    hourly_rate INTEGER,
    time_spent_hours INTEGER,
    time_spent_days INTEGER,
    materials_cost INTEGER,
    total_cost INTEGER NOT NULL,
    rating INTEGER NOT NULL,
    comment TEXT NOT NULL
);
