from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool
from langchain_openai import ChatOpenAI
import requests
import os

# 演示用的API配置（请在实际使用时替换为真实的API密钥）
DEMO_API_KEY = "sk-demo-key-for-testing-12345abcdef"  # 演示密钥
DEMO_BASE_URL = "https://api.openai.com/v1"  # 可以改为其他兼容API

@tool
def get_weather(city: str) -> str:
    """Get current weather for a given city."""
    # 演示用的天气API密钥
    weather_api_key = "demo_weather_key"
    
    # 如果没有真实API密钥，返回模拟数据
    if weather_api_key == "demo_weather_key":
        return f"Weather in {city}: sunny, 25°C (demo data - real API would provide actual weather)"
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}"
    
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
    # 使用演示配置（在安全测试中会被Mock替换）
    llm = ChatOpenAI(
        model="gpt-3.5-turbo", 
        temperature=0.7,
        openai_api_key=DEMO_API_KEY,
        openai_api_base=DEMO_BASE_URL
    )
    
    tools = [get_weather, calculate]
    
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    
    return agent

def main():
    print("🤖 创建Agent...")
    agent = create_agent()
    
    print("📝 Agent创建完成！")
    print("💡 这是一个包含安全漏洞的演示Agent")
    print("⚠️  已知漏洞：")
    print("   - eval()函数代码注入")
    print("   - 直接用户输入无验证")
    print("   - F-string格式化注入")
    print()
    
    # Example with direct user input (vulnerable)
    user_input = input("What would you like to know? (天气/计算/其他): ")
    
    # Vulnerable prompt formatting
    prompt = f"Please help me with this request: {user_input}"
    
    print(f"🔍 发送给Agent的提示词: {prompt}")
    print("⏳ Agent处理中...")
    
    try:
        response = agent.run(prompt)
        print(f"🤖 Agent回复: {response}")
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()