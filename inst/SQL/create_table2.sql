CREATE TABLE junction_config (
    id SERIAL PRIMARY KEY,
    num_lanes INT DEFAULT 1,
    lane_north_stright INT DEFAULT 1,
    lane_south_stright INT DEFAULT 1,
    lane_east_stright INT DEFAULT 1,
    lane_west_stright INT DEFAULT 1,
    lane_north_right INT DEFAULT 0,
    lane_south_right INT DEFAULT 0,
    lane_east_right INT DEFAULT 0,
    lane_west_right INT DEFAULT 0,
    lane_north_left INT DEFAULT 0,
    lane_south_left INT DEFAULT 0,
    lane_east_left INT DEFAULT 0,
    lane_west_left INT DEFAULT 0,
    lane_north_right_stright INT DEFAULT 0,
    lane_south_right_stright INT DEFAULT 0,
    lane_east_right_stright INT DEFAULT 0,
    lane_west_right_stright INT DEFAULT 0,
    lane_north_left_stright INT DEFAULT 0,
    lane_south_left_stright INT DEFAULT 0,
    lane_east_left_stright INT DEFAULT 0,
    lane_west_left_stright INT DEFAULT 0,
    has_left_turn_lane BOOLEAN DEFAULT FALSE,
    has_bus_cycle_lane BOOLEAN DEFAULT FALSE,
    has_pedestrian_crossing BOOLEAN DEFAULT FALSE,
    pedestrian_crossing_duration INT,
    crossing_requests_per_hour INT,
    prioritised_flow VARCHAR(20)
)
CREATE TABLE traffic_flow_north (
    id SERIAL PRIMARY KEY,
    vehicles_per_hour_enter_north INT NOT NULL,
    vehicles_per_hour_exit_south INT NOT NULL,
    vehicles_per_hour_exit_west INT NOT NULL,
    vehicles_per_hour_exit_east INT NOT NULL
);
CREATE TABLE traffic_flow_south (
    id SERIAL PRIMARY KEY,
    vehicles_per_hour_exit_north INT NOT NULL,
    vehicles_per_hour_enter_south INT NOT NULL,
    vehicles_per_hour_exit_west INT NOT NULL,
    vehicles_per_hour_exit_east INT NOT NULL
);
CREATE TABLE traffic_flow_east (
    id SERIAL PRIMARY KEY,
    vehicles_per_hour_exit_north INT NOT NULL,
    vehicles_per_hour_exit_south INT NOT NULL,
    vehicles_per_hour_exit_west INT NOT NULL,
    vehicles_per_hour_enter_east INT NOT NULL
);
CREATE TABLE traffic_flow_west (
    id SERIAL PRIMARY KEY,
    vehicles_per_hour_exit_north INT NOT NULL,
    vehicles_per_hour_exit_south INT NOT NULL,
    vehicles_per_hour_enter_west INT NOT NULL,
    vehicles_per_hour_exit_east INT NOT NULL
);
CREATE TABLE traffic_light_sequence (
    id SERIAL PRIMARY KEY,
    junction_id INT REFERENCES junction(id),
    direction VARCHAR(20) NOT NULL, -- Direction of the light (e.g., North, South)
    green_duration INT,
    red_duration INT,
    priority INT -- Priority of the traffic light sequence (0-4)
);
CREATE TABLE traffic_simulation_result (
    id SERIAL PRIMARY KEY,
    junction_id INT REFERENCES junction(id),
    average_wait_time INT,
    max_wait_time INT,
    max_queue_length INT
);
