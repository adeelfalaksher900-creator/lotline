// Tool: source_alert
MATCH (d:Document)-[:ABOUT]->(l:Lot {id:$lot_id}) RETURN d.id AS source_id
