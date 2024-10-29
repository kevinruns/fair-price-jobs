DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS tradesmen;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS user_groups;
DROP TABLE IF EXISTS group_tradesmen;
DROP TABLE IF EXISTS  join_requests;


-- users
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    postcode TEXT NOT NULL,
    hash TEXT NOT NULL
);

-- groups
CREATE TABLE groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    postcode TEXT NOT NULL
);

-- Junction table for user-group relationship
CREATE TABLE user_groups (
    user_id INTEGER,
    group_id INTEGER,
    status TEXT NOT NULL CHECK(status IN ('creator', 'admin', 'member')) DEFAULT 'member',
    PRIMARY KEY (user_id, group_id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE
);

-- tradesmen
CREATE TABLE tradesmen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade TEXT NOT NULL,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    postcode TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    email TEXT
);

-- New junction table for group-tradesman relationship
CREATE TABLE group_tradesmen (
    group_id INTEGER,
    tradesman_id INTEGER,
    PRIMARY KEY (group_id, tradesman_id),
    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
    FOREIGN KEY (tradesman_id) REFERENCES tradesmen (id) ON DELETE CASCADE
);

-- New table for jobs
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    tradesman_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    description TEXT NOT NULL,
    call_out_fee DECIMAL(10, 2),
    hourly_rate DECIMAL(10, 2),
    daily_rate DECIMAL(10, 2),
    total_cost DECIMAL(10, 2),
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    FOREIGN KEY (tradesman_id) REFERENCES tradesmen (id) ON DELETE CASCADE
);


-- New table for requests to join a table; for now keep simple; don't store old requests
CREATE TABLE join_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
--    status TEXT NOT NULL CHECK(status IN ('pending', 'approved', 'declined')) DEFAULT 'pending',
--    request_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
    UNIQUE (user_id, group_id)
);


