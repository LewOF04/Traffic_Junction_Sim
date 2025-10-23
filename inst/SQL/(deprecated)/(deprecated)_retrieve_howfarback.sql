SELECT efficiency_score
FROM efficiency_score_table
ORDER BY created_time DESC
LIMIT 1 OFFSET ${howFarBack};