--Retrieve all junction config with simulation results
SELECT 
    jc.*, 
    tsr.average_wait_time, 
    tsr.max_wait_time, 
    tsr.max_queue_length
FROM junction_config jc
LEFT JOIN traffic_simulation_result tsr 
    ON jc.id = tsr.junction_id;
--Get traffic flow data for specific junction(e.g. junction id = 1)
-- Northbound Traffic Flow
SELECT * FROM traffic_flow_north WHERE junction_id = ?;

-- Southbound Traffic Flow
SELECT * FROM traffic_flow_south WHERE junction_id = ?;

-- Eastbound Traffic Flow
SELECT * FROM traffic_flow_east WHERE junction_id = ?;

-- Westbound Traffic Flow
SELECT * FROM traffic_flow_west WHERE junction_id = ?;

-- Total Entering Vehicles 
WITH 
north AS (SELECT junction_id, SUM(vehicles_per_hour_enter_north) AS enter_north FROM traffic_flow_north GROUP BY junction_id),
south AS (SELECT junction_id, SUM(vehicles_per_hour_enter_south) AS enter_south FROM traffic_flow_south GROUP BY junction_id),
east  AS (SELECT junction_id, SUM(vehicles_per_hour_enter_east) AS enter_east FROM traffic_flow_east GROUP BY junction_id),
west  AS (SELECT junction_id, SUM(vehicles_per_hour_enter_west) AS enter_west FROM traffic_flow_west GROUP BY junction_id)

SELECT 
    jc.id AS junction_id,
    COALESCE(n.enter_north, 0) + 
    COALESCE(s.enter_south, 0) + 
    COALESCE(e.enter_east, 0) + 
    COALESCE(w.enter_west, 0) AS total_entering
FROM junction_config jc
LEFT JOIN north n ON jc.id = n.junction_id
LEFT JOIN south s ON jc.id = s.junction_id
LEFT JOIN east e ON jc.id = e.junction_id
LEFT JOIN west w ON jc.id = w.junction_id;
