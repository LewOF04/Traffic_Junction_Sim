SELECT
  jc.*,
  tfn.*,
  tfs.*,
  tfe.*,
  tfw.*
FROM junction_config jc
JOIN traffic_flow_north tfn ON jc.id = tfn.junction_id
JOIN traffic_flow_south tfs ON jc.id = tfs.junction_id
JOIN traffic_flow_east tfe ON jc.id = tfe.junction_id
JOIN traffic_flow_west tfw ON jc.id = tfw.junction_id
WHERE
  -- North direction traffic flow
  tfn.vehicles_per_hour_enter_north = [north_enter_value] AND
  tfn.vehicles_per_hour_exit_south = [north_exit_south_value] AND
  tfn.vehicles_per_hour_exit_west = [north_exit_west_value] AND
  tfn.vehicles_per_hour_exit_east = [north_exit_east_value] AND
  -- South direction traffic flow
  tfs.vehicles_per_hour_enter_south = [south_enter_value] AND
  tfs.vehicles_per_hour_exit_north = [south_exit_north_value] AND
  tfs.vehicles_per_hour_exit_west = [south_exit_west_value] AND
  tfs.vehicles_per_hour_exit_east = [south_exit_east_value] AND
  -- East direction traffic flow
  tfe.vehicles_per_hour_enter_east = [east_enter_value] AND
  tfe.vehicles_per_hour_exit_north = [east_exit_north_value] AND
  tfe.vehicles_per_hour_exit_south = [east_exit_south_value] AND
  tfe.vehicles_per_hour_exit_west = [east_exit_west_value] AND
  -- West direction traffic flow
  tfw.vehicles_per_hour_enter_west = [west_enter_value] AND
  tfw.vehicles_per_hour_exit_north = [west_exit_north_value] AND
  tfw.vehicles_per_hour_exit_south = [west_exit_south_value] AND
  tfw.vehicles_per_hour_exit_east = [west_exit_east_value];