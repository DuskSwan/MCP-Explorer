# -*- coding: utf-8 -*-

'''
Brave Search是一个隐私保护的搜索引擎，提供API接口供开发者使用。官网 https://brave.com/search/api/
采用langchain提供的接口工具来调用Brave Search，相关文档见 
  https://python.langchain.com/docs/integrations/tools/brave_search/
  https://python.langchain.com/api_reference/community/tools/langchain_community.tools.brave_search.tool.BraveSearch.html

'''
import ast
from langchain_community.tools import BraveSearch

import os
from dotenv import load_dotenv
load_dotenv()
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")

from mcp.server.fastmcp import FastMCP
mcp = FastMCP("wallpaper-server")

@mcp.tool()
def search_query_tool(query: str, 
                      country: str = "ALL",
                      search_lang: str = "en",
                      count: int = 3,
                      safesearch: str = "off",
                    ) -> str:
    '''
    search queries through Brave Search API

    params:
        query: str, keyword to search
        country: str, country code, default "ALL"
        search_lang: str, search language, default "en". For Chinese use "zh-hans" or "zh-hant".
        count: int, number of results to return, default 3
        safesearch: str, filters search results for adult content. Available value: "off", "moderate", "strict".
    
    return:
        response: str, search result or error message. Search result is string of a list of dicts, each dict contains a web page result.
    '''
    try:
        response = search_query(query, 
                                country=country,
                                search_lang=search_lang,
                                count=count,
                                safesearch=safesearch,
                               )
        return response
    except Exception as e:
        return f"Error: {e}"


def search_query(query, 
                 country="ALL",
                 search_lang="en",
                 count=3,
                 safesearch="off",
                 show_results=False,
                ):
    params = {
        "country": country,
        "search_lang": search_lang,
        "count": count,
        "safesearch": safesearch,
    }
    tool = BraveSearch.from_api_key(
        api_key=BRAVE_API_KEY, 
        search_kwargs=params,
    )

    response = tool.run(query)
    response = response.encode('utf-8').decode('unicode_escape') # transform unicode to utf-8
    '''
    result format: string of a list of dicts
    each dict contains:
        title: str, title of the result
        link: str, link to the result
        snippet: str, snippet of the result
    '''
    
    if show_results:
        print("Brave Search Results:")
        res_dicts = ast.literal_eval(response)
        for i, res in enumerate(res_dicts):
            print("-" * 80)
            print(f"Result {i+1}:")
            print(f"Title: {res['title']}")
            print(f"Link: {res['link']}")
            print(f"Snippet: {res['snippet']}")
            print("-" * 80)
    return response

def test():
    res = search_query("奥巴马生平", count=3, show_results=True)
    print(res)
    # zhres = res.encode().decode('unicode_escape')
    # print(zhres)

if __name__ == "__main__":
    mcp.run(transport='stdio')
    # test()