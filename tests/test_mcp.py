import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

@unittest.skipUnless(importlib.util.find_spec('mcp'),'Optional MCP SDK not installed')
class MCPTests(unittest.IsolatedAsyncioTestCase):
 async def test_stdio_tools_and_invalid_paid_node(self):
  from mcp import ClientSession,StdioServerParameters
  from mcp.client.stdio import stdio_client
  server=StdioServerParameters(command=sys.executable,args=['-m','aigc_character_media.mcp_server'],env={'PYTHONPATH':str(ROOT/'src')})
  async with stdio_client(server) as (read,write):
   async with ClientSession(read,write) as s:
    await s.initialize();r=await s.list_tools()
    self.assertEqual({t.name for t in r.tools},{'local_voice_health','synthesize_local_voice','local_video_health','submit_local_video','local_video_status'})
    denied=await s.call_tool('submit_local_video',{'workflow':{'1':{'class_type':'PaidVideoAPI','inputs':{}}}})
    self.assertTrue(denied.isError)
    r=await s.call_tool('local_voice_health',{});self.assertFalse(r.isError)
if __name__=='__main__':unittest.main()
