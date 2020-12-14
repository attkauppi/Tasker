DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS roles;
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    role_name TEXT UNIQUE,
    default_role BOOLEAN,
    permissions INTEGER
);
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE, password TEXT,
    email TEXT,
    created TIMESTAMP WITHOUT TIME ZONE,
    last_seen TIMESTAMP WITHOUT TIME ZONE,
    role_id INTEGER,
    avatar_hash TEXT,
    FOREIGN KEY (role_id) REFERENCES roles (id));
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    content TEXT
);
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    creator_id INTEGER NOT NULL,
    title TEXT,
    description TEXT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    done BOOLEAN,
    FOREIGN KEY (creator_id) REFERENCES users (id)
);
