"""Optional official MCP SDK wrapper for working local adapters. No media placeholders."""
from .local_video import LocalVideoProvider
from .local_voice import health,synthesize

def main():
    from mcp.server.fastmcp import FastMCP
    mcp=FastMCP('aigc-character-media')
    @mcp.tool()
    def local_voice_health()->dict:
        return health()
    @mcp.tool()
    def synthesize_local_voice(text:str,speaker:str,output_dir:str='outputs/local-voice',max_duration_sec:float|None=None)->dict:
        return synthesize(text,speaker,output_dir,max_duration_sec)
    @mcp.tool()
    def local_video_health()->dict:
        return LocalVideoProvider().health()
    @mcp.tool()
    def submit_local_video(workflow:dict)->dict:
        return LocalVideoProvider().submit(workflow)
    @mcp.tool()
    def local_video_status(prompt_id:str)->dict:
        return LocalVideoProvider().status(prompt_id)
    mcp.run(transport='stdio')
if __name__=='__main__':main()
