DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS team_members;
DROP TABLE IF EXISTS team_roles;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS message;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS team_tasks;

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    role_name TEXT UNIQUE,
    default_role BOOLEAN,
    permissions INTEGER
);
CREATE TABLE team_roles (
    id SERIAL PRIMARY KEY,
    team_role_name TEXT,
    default_role BOOLEAN,
    team_permissions INTEGER
);
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    title TEXT,
    description TEXT,
    CREATED TIMESTAMP WITHOUT TIME ZONE,
    MODIFIED TIMESTAMP WITHOUT TIME ZONE
);
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    email TEXT,
    about_me TEXT,
    confirmed BOOLEAN,
    created TIMESTAMP WITHOUT TIME ZONE,
    last_seen TIMESTAMP WITHOUT TIME ZONE,
    role_id INTEGER,
    avatar_hash TEXT,
    FOREIGN KEY (role_id) REFERENCES roles (id)
);
CREATE TABLE team_members (
    id SERIAL PRIMARY KEY,
    team_id INTEGER NOT NULL,
    team_member_id INTEGER NOT NULL,
    team_role_id INTEGER NOT NULL,
    FOREIGN KEY (team_id) REFERENCES teams (id),
    FOREIGN KEY (team_member_id) REFERENCES users (id),
    FOREIGN KEY (team_role_id) REFERENCES team_roles (id)
);
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    content TEXT
);
CREATE TABLE message (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL,
    recipient_id INTEGER NOT NULL,
    body TEXT,
    timestamp TIMESTAMP WITHOUT TIME ZONE,
    FOREIGN KEY (sender_id) REFERENCES users (id),
    FOREIGN KEY (sender_id) REFERENCES users (id)
)
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title TEXT,
    description TEXT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    done BOOLEAN,
    creator_id INTEGER NOT NULL,
    position TEXT,
    priority BOOLEAN DEFAULT FALSE,
    board INTEGER,
    is_team_task BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (creator_id) REFERENCES users (id)
);
CREATE TABLE team_tasks (
    id SERIAL PRIMARY KEY,
    team_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    doing INTEGER NOT NULL,
    assigned BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (team_id) REFERENCES teams (id),
    FOREIGN KEY (task_id) REFERENCES tasks (id),
    FOREIGN KEY (doing) REFERENCES team_members (id)
)