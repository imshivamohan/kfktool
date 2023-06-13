-- Create the users table to store user information
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the user_config table to store user configurations
CREATE TABLE IF NOT EXISTS user_config (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) NOT NULL,
    api_secret VARCHAR(255) NOT NULL,
    schema_api_key VARCHAR(255) NOT NULL,
    schema_api_secret VARCHAR(255) NOT NULL,
    schema_url VARCHAR(255) NOT NULL,
    bootstrap_server VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the topic_cgroup_config table to store topic and consumer group configurations
CREATE TABLE IF NOT EXISTS topic_cgroup_config (
    id SERIAL PRIMARY KEY,
    topic VARCHAR(255) NOT NULL,
    consumer_group VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
