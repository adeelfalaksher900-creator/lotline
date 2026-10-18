// Tool: history
MATCH (d:Decision) RETURN properties(d) AS decision ORDER BY d.at DESC LIMIT 30
