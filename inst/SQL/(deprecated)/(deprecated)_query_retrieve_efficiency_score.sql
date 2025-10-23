-- Query to get the efficiency score of the xth last junction added (where x is a parameter)
SELECT id, efficiency_score
FROM efficiency_score_table
ORDER BY created_time DESC
OFFSET (? - 1) LIMIT 1;

-- Query to get efficiency score of last 5 junctions
SELECT id, efficiency_score
FROM efficiency_score_table
ORDER BY created_time DESC
LIMIT ?;

-- Query to get the efficiency score of the current junction (the last one added to the DB)
SELECT id, efficiency_score
FROM efficiency_score_table
ORDER BY created_time DESC
LIMIT 1;