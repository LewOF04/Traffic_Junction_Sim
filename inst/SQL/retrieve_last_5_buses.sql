SELECT north_buses_per_hour, east_buses_per_hour, south_buses_per_hour, west_buses_per_hour
FROM junction_config
WHERE junction_id = ?;