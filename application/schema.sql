DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS tasks;
CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT);
CREATE TABLE messages (id SERIAL PRIMARY KEY, content TEXT);
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    creator_id INTEGER NOT NULL,
    title TEXT,
    description TEXT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    done BOOLEAN,
    FOREIGN KEY (creator_id) REFERENCES users (id)
);