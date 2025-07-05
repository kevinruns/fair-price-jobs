DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS tradesmen;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS user_groups;
DROP TABLE IF EXISTS group_tradesmen;
DROP TABLE IF EXISTS user_tradesmen;
-- DROP TABLE IF EXISTS  join_requests;


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
    postcode TEXT NOT NULL,
    description TEXT
);

-- Junction table for user-group relationship
CREATE TABLE user_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    group_id INTEGER,
    status TEXT NOT NULL CHECK(status IN ('creator', 'admin', 'member', 'pending')) DEFAULT 'pending',
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
    UNIQUE (user_id, group_id)
);

-- tradesmen
CREATE TABLE tradesmen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade TEXT NOT NULL,
    first_name TEXT,
    family_name TEXT NOT NULL,
    company_name TEXT,
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

-- New junction table for user-tradesman relationship
CREATE TABLE user_tradesmen (
    user_id INTEGER,
    tradesman_id INTEGER,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, tradesman_id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (tradesman_id) REFERENCES tradesmen (id) ON DELETE CASCADE
);

-- New table for jobs and quotes
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    tradesman_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('job', 'quote')) DEFAULT 'job',
    date_started TEXT,
    date_finished TEXT,
    date_requested TEXT,
    date_received TEXT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    call_out_fee INTEGER NULL,
    materials_fee INTEGER NULL,
    hourly_rate INTEGER NULL,
    hours_worked REAL NULL,
    hours_estimated REAL NULL,
    daily_rate INTEGER NULL,
    days_worked REAL NULL,
    days_estimated REAL NULL,
    total_cost INTEGER NULL CHECK (total_cost IS NULL OR total_cost >= 0),
    total_quote INTEGER NULL CHECK (total_quote IS NULL OR total_quote >= 0),
    rating INTEGER NULL CHECK (rating IS NULL OR (rating >= 1 AND rating <= 5)),
    status TEXT CHECK (status IN ('pending', 'accepted', 'declined')) DEFAULT 'pending',
    FOREIGN KEY (tradesman_id) REFERENCES tradesmen (id) ON DELETE CASCADE
);


-- -- New table for requests to join a table; for now keep simple; don't store old requests
-- CREATE TABLE join_requests (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     user_id INTEGER NOT NULL,
--     group_id INTEGER NOT NULL,
-- --    status TEXT NOT NULL CHECK(status IN ('pending', 'approved', 'declined')) DEFAULT 'pending',
-- --    request_date DATETIME DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
--     FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
--     UNIQUE (user_id, group_id)
-- );


