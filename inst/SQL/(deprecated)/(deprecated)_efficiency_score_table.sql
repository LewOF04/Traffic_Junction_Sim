CREATE TABLE IF NOT EXISTS efficiency_score_table(
    id TEXT PRIMARY KEY,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    efficiency_score INT,
    FOREIGN KEY(id) REFERENCES junction_config(id)
);
