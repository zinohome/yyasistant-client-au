import yfinance as yf
import chainlit as cl
import plotly
import datetime
import os
import requests
from config import config_from_dotenv

# 修正.env路径为项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg = config_from_dotenv(os.path.join(PROJECT_ROOT, '.env'), read_from_file=True)

query_stock_price_def = {
    "name": "query_stock_price",
    "description": "Queries the latest stock price information for a given stock symbol.",
    "parameters": {
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "The stock symbol to query (e.g., 'AAPL' for Apple Inc.)",
            },
            "period": {
                "type": "string",
                "description": "The time period for which to retrieve stock data (e.g., '1d' for one day, '1mo' for one month)",
            },
        },
        "required": ["symbol", "period"],
    },
}


async def query_stock_price_handler(symbol, period):
    """
    Queries the latest stock price information for a given stock symbol.
    """
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        if hist.empty:
            return {"error": "No data found for the given symbol."}
        return hist.to_json()

    except Exception as e:
        return {"error": str(e)}


query_stock_price = (query_stock_price_def, query_stock_price_handler)

draw_plotly_chart_def = {
    "name": "draw_plotly_chart",
    "description": "Draws a Plotly chart based on the provided JSON figure and displays it with an accompanying message.",
    "parameters": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "The message to display alongside the chart",
            },
            "plotly_json_fig": {
                "type": "string",
                "description": "A JSON string representing the Plotly figure to be drawn",
            },
        },
        "required": ["message", "plotly_json_fig"],
    },
}


async def draw_plotly_chart_handler(message: str, plotly_json_fig):
    fig = plotly.io.from_json(plotly_json_fig)
    elements = [cl.Plotly(name="chart", figure=fig, display="inline")]

    await cl.Message(content=message, elements=elements).send()


draw_plotly_chart = (draw_plotly_chart_def, draw_plotly_chart_handler)

get_current_time_def = {
    "name": "get_current_time",
    "description": "获取当前时间，返回格式为%Y-%m-%d %H:%M:%S。",
    "parameters": {"type": "object", "properties": {}, "required": []},
}
async def get_current_time_handler():
    """
    获取当前时间，返回格式为%Y-%m-%d %H:%M:%S
    """
    now = datetime.datetime.now()
    return {"current_time": now.strftime("%Y-%m-%d %H:%M:%S")}

get_current_time = (get_current_time_def, get_current_time_handler)

from tavily import TavilyClient
tavily_search_def = {
    "name": "tavily_search",
    "description": "调用tavily接口搜索关键词，返回5条相关结果。",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "检索关键词"}
        },
        "required": ["query"]
    },
}
async def tavily_search_handler(query: str):
    """
    调用tavily接口搜索，返回5条结果。
    """
    api_key = cfg.TAVILY_API_KEY
    if not api_key:
        return {"error": "TAVILY_API_KEY未设置"}
    try:
        client = TavilyClient(api_key)
        response = client.search(
            query=query,
            max_results=5,
            time_range="day",
            include_favicon=True,
            country="china",
            include_answer=True
        )
        return {"results": response.get("results", response)}
    except Exception as e:
        return {"error": str(e)}

tavily_search = (tavily_search_def, tavily_search_handler)

amap_query_def = {
    "name": "amap_query",
    "description": "根据城市名查询该地的实时天气情况（数据来自高德平台）",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "城市名称（如'北京'）"}
        },
        "required": ["city"]
    }
}

async def amap_query_handler(city: str) -> str:
    api_key = cfg.AMAP_MAPS_API_KEY
    if not api_key:
        return "请先配置AMAP_MAPS_API_KEY环境变量。"
    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {"key": api_key, "city": city, "extensions": "base"}
    try:
        resp = requests.get(url, params=params, timeout=8)
        data = resp.json()
        if data.get("status") == "1" and data.get("lives"):
            weather_data = data["lives"][0]
            return f"{weather_data['city']}当前天气：{weather_data['weather']}，温度：{weather_data['temperature']}℃，风向：{weather_data['winddirection']}，风力：{weather_data['windpower']}级"
        else:
            return "未查到该城市天气信息。"
    except Exception as e:
        return f"请求天气接口异常: {e}"


amap_query = (amap_query_def, amap_query_handler)
#tools = [query_stock_price, draw_plotly_chart, get_current_time, tavily_search, amap_query]
tools = [get_current_time, tavily_search, amap_query]
#tools = [query_stock_price, draw_plotly_chart]