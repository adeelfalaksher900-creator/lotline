import asyncio,json,os,sys
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    async with stdio_client(StdioServerParameters(command=sys.executable,args=['-m','backend.mcp_server'],env={**os.environ})) as (read,write):
        async with ClientSession(read,write) as client:
            await client.initialize()
            listed=await client.list_tools()
            names=[t.name for t in listed.tools]
            assert set(names)=={'investigate','compare_depth','explain_path','history'},names
            result=await client.call_tool('compare_depth',{'lot_id':'LOT-SM-2407'})
            data=result.structuredContent
            if data is None:
                data=json.loads(result.content[0].text)
            assert data['totals']['units']==1180, data
            unknown=await client.call_tool('investigate',{'lot_id':'LOT-NOT-REAL'})
            unknown_data=unknown.structuredContent or json.loads(unknown.content[0].text)
            assert unknown_data['outcome']=='unknown_lot'
            print(json.dumps({'mcp':'passed','tools':names,'units':data['totals']['units'],'unknown':'passed'}))
asyncio.run(main())
