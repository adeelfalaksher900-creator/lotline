// Tool: documents
MATCH (d:Document) WHERE d.id IN $ids RETURN properties(d) AS document ORDER BY d.id
