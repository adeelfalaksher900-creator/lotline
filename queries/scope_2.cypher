// Tool: scope_2
MATCH p=(root:Lot {id:$lot_id})-[:INPUT_TO*0..2]->(lot:Lot)
OPTIONAL MATCH (lot)-[:DISPATCHED]->(shipment:Shipment)-[:DELIVERED_TO]->(site:Site)
RETURN lot.id AS lot_id, lot.name AS lot_name,
       [n IN nodes(p) | n.id] AS path,
       [r IN relationships(p) | r.source_id] AS source_ids,
       [r IN relationships(p) | r.evidence] AS evidence,
       length(p) AS hops,
       properties(shipment) AS shipment,
       properties(site) AS site
ORDER BY hops, lot_id
LIMIT 501
