CREATE TABLE IF NOT EXISTS junction_config (
    junction_id TEXT PRIMARY KEY, 

    north_left_right_lane INT DEFAULT 0,
    north_left_right_straight_lane INT DEFAULT 0,
    north_left_lane_count INT DEFAULT 0,
    north_right_lane_count INT DEFAULT 0,
    north_straight_right_lane_count INT DEFAULT 0,
    north_straight_left_lane_count INT DEFAULT 0,
    north_straight_lane_count INT DEFAULT 1,

    north_priority INT DEFAULT 0,
    north_buses_per_hour INT DEFAULT 0,

    east_left_right_lane INT DEFAULT 0,
    east_left_right_straight_lane INT DEFAULT 0,
    east_left_lane_count INT DEFAULT 0,
    east_right_lane_count INT DEFAULT 0,
    east_straight_right_lane_count INT DEFAULT 0,
    east_straight_left_lane_count INT DEFAULT 0,
    east_straight_lane_count INT DEFAULT 0,

    east_priority INT DEFAULT 0,
    east_buses_per_hour INT DEFAULT 0,

    south_left_right_lane INT DEFAULT 0,
    south_left_right_straight_lane INT DEFAULT 0,
    south_left_lane_count INT DEFAULT 0,
    south_right_lane_count INT DEFAULT 0,
    south_straight_right_lane_count INT DEFAULT 0,
    south_straight_left_lane_count INT DEFAULT 0,
    south_straight_lane_count INT DEFAULT 0,

    south_priority INT DEFAULT 0,
    south_buses_per_hour INT DEFAULT 0,

    west_left_right_lane INT DEFAULT 0,
    west_left_right_straight_lane INT DEFAULT 0,
    west_left_lane_count INT DEFAULT 0,
    west_right_lane_count INT DEFAULT 0,
    west_straight_right_lane_count INT DEFAULT 0,
    west_straight_left_lane_count INT DEFAULT 0,
    west_straight_lane_count INT DEFAULT 0,

    west_priority INT DEFAULT 0,
    west_buses_per_hour INT DEFAULT 0,

    has_pedestrian_crossing INT DEFAULT 0,
    pedestrian_crossing_duration INT DEFAULT 0,
    crossing_requests_per_hour INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS traffic_flow_north (
    junction_id TEXT PRIMARY KEY,
    vehicles_per_hour_enter_north INT NOT NULL,
    vehicles_per_hour_exit_south INT NOT NULL,
    vehicles_per_hour_exit_west INT NOT NULL,
    vehicles_per_hour_exit_east INT NOT NULL,
    FOREIGN KEY (junction_id) REFERENCES junction_config(junction_id) 
);

CREATE TABLE IF NOT EXISTS traffic_flow_south (
    junction_id TEXT PRIMARY KEY,
    vehicles_per_hour_exit_north INT NOT NULL,
    vehicles_per_hour_enter_south INT NOT NULL,
    vehicles_per_hour_exit_west INT NOT NULL,
    vehicles_per_hour_exit_east INT NOT NULL,
    FOREIGN KEY (junction_id) REFERENCES junction_config(junction_id) 
);

CREATE TABLE IF NOT EXISTS traffic_flow_east (
    junction_id TEXT PRIMARY KEY,
    vehicles_per_hour_exit_north INT NOT NULL,
    vehicles_per_hour_exit_south INT NOT NULL,
    vehicles_per_hour_exit_west INT NOT NULL,
    vehicles_per_hour_enter_east INT NOT NULL,
    FOREIGN KEY (junction_id) REFERENCES junction_config(junction_id) 
);

CREATE TABLE IF NOT EXISTS traffic_flow_west (
    junction_id TEXT PRIMARY KEY,
    vehicles_per_hour_exit_north INT NOT NULL,
    vehicles_per_hour_exit_south INT NOT NULL,
    vehicles_per_hour_enter_west INT NOT NULL,
    vehicles_per_hour_exit_east INT NOT NULL,
    FOREIGN KEY (junction_id) REFERENCES junction_config(junction_id) 
);

CREATE TABLE IF NOT EXISTS traffic_light_sequence (
    junction_id TEXT PRIMARY KEY,
    direction TEXT NOT NULL, -- Direction of the light (e.g., North, South)
    green_duration INT,
    red_duration INT,
    vh_priority INT, -- Priority of the traffic light sequence (0-4)
    FOREIGN KEY (junction_id) REFERENCES junction_config(junction_id) 
);

CREATE TABLE IF NOT EXISTS traffic_simulation_result (
    junction_id TEXT PRIMARY KEY,
    average_wait_time INT NOT NULL,
    max_wait_time INT NOT NULL,
    max_queue_length INT NOT NULL,
    FOREIGN KEY (junction_id) REFERENCES junction_config(junction_id)
);

CREATE TABLE IF NOT EXISTS efficiency_score_table(
    junction_id TEXT PRIMARY KEY,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    efficiency_score INT DEFAULT 0,
    FOREIGN KEY (junction_id) REFERENCES junction_config(junction_id)
);