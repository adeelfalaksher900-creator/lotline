// Tool: dispatch_sources
MATCH (l:Lot)-[e:DISPATCHED]->(s:Shipment) WHERE s.id IN $ids RETURN s.id AS id,e.source_id AS source_id
