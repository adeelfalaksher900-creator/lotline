// Tool: resolve_lot
MATCH (l:Lot {id:$lot_id}) RETURN properties(l) AS lot
