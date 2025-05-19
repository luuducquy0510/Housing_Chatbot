from langchain_community.tools import DuckDuckGoSearchResults, TavilySearchResults

#web search tool
def web_search_tool(topic: str) -> dict:
    """Perform an online web search to retrieve the latest information about the given topic."""
    search = DuckDuckGoSearchResults(
        output_format="list",
        max_results=50
        )
    a = search.invoke(f"""{topic}""")
    return {"Search Results": a}

def web_search_tool_tavily(topic: str) -> dict:
    """Perform an online web search to retrieve the latest information about the given topic."""
    search = TavilySearchResults(
        max_results=5,
        include_answer=True,
        include_raw_content=True,
        include_images=True,
        )
    a = search.invoke(f"""{topic}""")
    return {"Search Results": a}