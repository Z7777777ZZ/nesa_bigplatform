from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool
from langchain_openai import ChatOpenAI
import requests
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

@tool
def get_weather(city: str) -> str:
    """Get current weather for a given city."""
    # 从环境变量获取API密钥
    api_key = os.getenv("WEATHER_API_KEY", "demo_key")
    
    # 如果没有真实API密钥，返回模拟数据
    if api_key == "demo_key":
        return f"Weather in {city}: sunny (demo data - set WEATHER_API_KEY for real data)"
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    
    try:
        response = requests.get(url)
        data = response.json()
        return f"Weather in {city}: {data.get('weather', [{}])[0].get('description', 'unknown')}"
    except:
        return f"Could not get weather for {city}"

@tool 
def calculate(expression: str) -> str:
    """Safely calculate mathematical expressions."""
    try:
        # WARNING: This is vulnerable to code injection
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"

def create_agent():
    # 从环境变量获取配置
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    
    if not api_key:
        raise ValueError("请设置OPENAI_API_KEY环境变量")
    
    llm_kwargs = {
        "model": "gpt-4o",
        "temperature": 0.7,
        "openai_api_key": api_key
    }
    
    # 如果设置了自定义base_url，添加到配置中
    if base_url:
        llm_kwargs["openai_api_base"] = base_url
    
    llm = ChatOpenAI(**llm_kwargs)
    
    tools = [get_weather, calculate]
    
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    
    return agent

def main():
    agent = create_agent()
    
    # Example with direct user input (vulnerable)
    user_input = input("What is the weather in Beijing? ")
    
    # Vulnerable prompt formatting
    prompt = f"Please help me with this request: {user_input}"
    
    try:
        response = agent.run(prompt)
        print(f"Agent response: {response}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()