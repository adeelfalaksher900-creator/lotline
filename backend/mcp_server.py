"""Read-only MCP tools. Run: python3 -m backend.mcp_server."""
import os
from typing import Annotated
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from .database import graph_for
from .tools import investigate as _investigate, compare_depth as _compare, decision_history

mcp = FastMCP('Lotline', instructions='Investigate fictional supply-chain lots using FalkorDB. All tools are read-only. Humans approve sandbox holds only in the web interface.')
WORKSPACE = os.environ.get('LOTLINE_MCP_WORKSPACE', '00000000000000000000000000000047')

@mcp.tool()
def investigate(lot_id: Annotated[str, Field(min_length=1,max_length=64)], depth: Annotated[int, Field(ge=1,le=6)] = 6) -> dict:
    """Trace a source lot through transformations to shipments, with evidence paths."""
    return _investigate(graph_for(WORKSPACE),lot_id,depth)

@mcp.tool()
def compare_depth(lot_id: Annotated[str, Field(min_length=1,max_length=64)]) -> dict:
    """Compare one-hop lookup with a complete six-hop traversal of the same lot."""
    return _compare(graph_for(WORKSPACE),lot_id)

@mcp.tool()
def explain_path(lot_id: Annotated[str, Field(min_length=1,max_length=64)], shipment_id: Annotated[str, Field(min_length=1,max_length=64)]) -> dict:
    """Return actual paths to one shipment. Missing evidence is not a safety finding."""
    result=_investigate(graph_for(WORKSPACE),lot_id,6)
    paths=[s for s in result['confirmed']+result['uncertain'] if s['id']==shipment_id]
    return {'lot_id':lot_id,'shipment_id':shipment_id,'paths':paths,'outcome':'path_found' if paths else 'no_path_in_graph'}

@mcp.tool()
def history() -> dict:
    """Read reviewed decisions in this MCP workspace. Never create or approve one."""
    return {'decisions':decision_history(graph_for(WORKSPACE))}

if __name__ == '__main__':
    mcp.run(transport='stdio')
