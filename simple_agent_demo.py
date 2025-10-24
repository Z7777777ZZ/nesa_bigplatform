from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool
from langchain_openai import ChatOpenAI
import requests
import os
import ast
import operator

# 演示用的API配置（请在实际使用时替换为真实的API密钥）
DEMO_API_KEY = "sk-cNPnRmWy4yWFKTaZ5383FeE01e7446919d8e4e7e32366240"  # 演示密钥
DEMO_BASE_URL = "https://api.gpt.ge/v1"  # 可以改为其他兼容API

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
        # 安全的数学表达式计算，避免代码注入
        allowed_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
        }
        
        def safe_eval(node):
            if isinstance(node, ast.Expression):
                return safe_eval(node.body)
            elif isinstance(node, ast.Constant):  # Python 3.8+
                return node.value
            elif isinstance(node, ast.Num):  # Python < 3.8
                return node.n
            elif isinstance(node, ast.BinOp):
                left = safe_eval(node.left)
                right = safe_eval(node.right)
                return allowed_operators[type(node.op)](left, right)
            elif isinstance(node, ast.UnaryOp):
                operand = safe_eval(node.operand)
                return allowed_operators[type(node.op)](operand)
            else:
                raise ValueError(f"Unsupported operation: {type(node)}")
        
        tree = ast.parse(expression, mode='eval')
        result = safe_eval(tree)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"

def create_agent():
    # 使用演示配置（在安全测试中会被Mock替换）
    llm = ChatOpenAI(
        model="gpt-4o", 
        temperature=0.7,
        openai_api_key=DEMO_API_KEY,
        openai_api_base=DEMO_BASE_URL
    )
    
    tools = [get_weather, calculate]
    
    # 使用最简单的agent创建方式
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3
    )
    
    return agent

def main():
    print("🤖 创建Agent...")
    agent = create_agent()
    
    # 预设的测试问题，不需要用户输入
    test_questions = [
        "What is the weather in Beijing?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*50}")
        print(f"🧪 测试 {i}: {question}")
        print(f"🔍 发送给Agent的提示词: {question}")
        print("⏳ Agent处理中...")
        
        try:
            response = agent.run(question)
            print(f"🤖 Agent回复: {response}")
        except Exception as e:
            print(f"❌ 错误: {e}")
        
        print(f"{'='*50}")
    
    print("\n✅ 所有测试完成！")

if __name__ == "__main__":
    main()