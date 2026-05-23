from tools.decorators import tool


@tool(name="get_weather", description="查询指定城市的天气")
def get_weather(city: str):
    return f"{city}的天气晴朗，气温25℃"