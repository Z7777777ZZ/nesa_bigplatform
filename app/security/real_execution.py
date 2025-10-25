import subprocess
import tempfile
import os
import sys
from typing import Dict, Any
import time
import base64

class RealAgentExecutor:
    """真实执行Agent代码的类"""
    
    def __init__(self, timeout: int = 60):
        self.timeout = timeout
    
    def execute_agent_with_input(self, file_path: str, user_input: str) -> Dict[str, Any]:
        """真实执行Agent并获取结果"""
        print(f"🔍 开始执行Agent测试: {file_path}")
        print(f"📝 用户输入: {user_input[:100]}...")
        
        try:
            # 读取原始Agent代码
            with open(file_path, 'r', encoding='utf-8') as f:
                original_code = f.read()
            
            print(f"📄 代码长度: {len(original_code)} 字符")
            
            # 创建测试脚本
            test_script = self._create_test_script(original_code, user_input)
            
            print(f"📝 测试脚本创建完成，长度: {len(test_script)} 字符")
            
            # 执行测试脚本
            print("🚀 开始执行测试脚本...")
            result = self._execute_script(test_script)
            
            print(f"✅ 执行完成，返回码: {result['return_code']}")
            print(f"⏱️  执行时间: {result['execution_time']:.2f}秒")
            
            # 不限制输出长度，显示完整结果
            stdout = result["stdout"]
            stderr = result["stderr"]
            
            return {
                "success": result["return_code"] == 0,
                "output": stdout,
                "error": stderr,
                "execution_time": result["execution_time"],
                "api_called": self._detect_api_calls(result["stdout"] + result["stderr"]),
                "return_code": result["return_code"]
            }
            
        except Exception as e:
            print(f"❌ 执行出错: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "execution_time": 0,
                "api_called": False,
                "return_code": -1
            }
    
    def _create_test_script(self, original_code: str, user_input: str) -> str:
        """创建包含用户输入的测试脚本"""
        
        # 硬编码API配置
        api_key = "sk-cNPnRmWy4yWFKTaZ5383FeE01e7446919d8e4e7e32366240"
        base_url = "https://api.gpt.ge/v1"
        
        print(f"🔑 使用硬编码API密钥: {api_key[:10]}...")
        print(f"🌐 使用硬编码Base URL: {base_url}")
        
        # 检查是否为攻击负载，如果是则进行代码注入
        if any(keyword in user_input.lower() for keyword in ["ignore", "override", "system prompt", "instructions"]):
            print("🔴 检测到攻击负载，进行代码注入...")
            
            # 修改原始代码，注入攻击载荷
            if "agent.run(question)" in original_code:
                print("🎯 找到 agent.run(question) 行，进行代码注入...")
                
                # 替换测试问题列表 - 使用更精确的匹配
                import re
                # 匹配多行的列表定义
                pattern = r'test_questions = \[\s*"[^"]*",\s*"[^"]*",\s*"[^"]*"\s*\]'
                replacement = 'test_questions = ["What is the weather in Beijing?"]'
                modified_code = re.sub(pattern, replacement, original_code, flags=re.DOTALL)
                
                # 如果上面的模式没匹配到，尝试更简单的模式
                if 'test_questions = [' in modified_code and modified_code.count('test_questions = ["What is the weather in Beijing?"]') == 0:
                    # 手动查找和替换
                    lines = modified_code.split('\n')
                    new_lines = []
                    in_test_questions = False
                    
                    for line in lines:
                        if 'test_questions = [' in line:
                            new_lines.append('    test_questions = ["What is the weather in Beijing?"]')
                            in_test_questions = True
                        elif in_test_questions and ']' in line:
                            in_test_questions = False
                            # 跳过这一行，因为已经在上面添加了完整的定义
                        elif not in_test_questions:
                            new_lines.append(line)
                    
                    modified_code = '\n'.join(new_lines)
                
                # 在循环中添加攻击载荷
                if "for i, question in enumerate(test_questions, 1):" in modified_code:
                    lines = modified_code.split('\n')
                    new_lines = []
                    
                    for line in lines:
                        new_lines.append(line)
                        if "for i, question in enumerate(test_questions, 1):" in line:
                            # 在循环开始后添加攻击载荷
                            new_lines.append('        # 代码注入攻击')
                            escaped_input = user_input.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
                            new_lines.append(f'        question = question + "\\n\\n{escaped_input}"')
                    
                    original_code = '\n'.join(new_lines)
                    print("✅ 代码注入完成")
                else:
                    print("⚠️ 未找到循环结构，使用原始代码")
            else:
                print("⚠️ 未找到 agent.run(question)，使用原始代码")
        
        # 使用base64编码来传递代码，避免字符串转义问题
        code_bytes = original_code.encode('utf-8')
        code_base64 = base64.b64encode(code_bytes).decode('utf-8')
        
        input_bytes = user_input.encode('utf-8')
        input_base64 = base64.b64encode(input_bytes).decode('utf-8')
        
        api_key_info = "有效" if len(api_key) > 10 else "未设置或无效"
        
        test_script = '''
import sys
import os
import time
import base64

print("=== NESA Agent 安全测试 - 真实执行模式 ===")
print("时间:", time.strftime('%Y-%m-%d %H:%M:%S'))

# 设置环境变量
os.environ['OPENAI_API_KEY'] = "''' + api_key + '''"
os.environ['OPENAI_BASE_URL'] = "''' + base_url + '''"

print("API Key设置:", "''' + api_key_info + '''")
print("Base URL:", "''' + base_url + '''")
print()

# 解码原始代码
code_base64 = "''' + code_base64 + '''"
original_code = base64.b64decode(code_base64).decode('utf-8')

# 解码用户输入
input_base64 = "''' + input_base64 + '''"
user_input_decoded = base64.b64decode(input_base64).decode('utf-8')

# Mock input函数来提供测试输入
def mock_input(prompt=""):
    print("🤖 Agent请求用户输入:", prompt)
    print("👤 用户输入:", user_input_decoded)
    return user_input_decoded

# 替换内置input函数
import builtins
original_input = builtins.input
builtins.input = mock_input

print("📁 开始执行Agent代码...")
print("-" * 50)

execution_start = time.time()

try:
    # 首先执行原始代码来定义函数和类
    print("📁 加载Agent代码...")
    exec(original_code)
    
    execution_time = time.time() - execution_start
    print("✅ 代码加载完成，耗时: {:.2f}秒".format(execution_time))
    
    # 检查是否有create_agent函数
    if 'create_agent' in globals():
        print("🤖 发现create_agent函数，跳过直接调用...")
        print("💡 代码已经通过exec()执行，如果有main()函数会自动运行")
    
    elif 'main' in globals():
        print("🚀 发现main函数，已通过exec()自动执行")
        print("💡 代码注入已在加载时完成")
    else:
        print("⚠️  未发现create_agent或main函数")
        print("💡 尝试直接测试可用的工具...")
        
        # 尝试找到并测试工具
        global_vars = globals()
        tools_found = []
        for name, obj in global_vars.items():
            if hasattr(obj, '__name__') and hasattr(obj, '__annotations__'):
                tools_found.append(name)
        
        if tools_found:
            print("🔧 发现工具函数:", ', '.join(tools_found))
            for tool_name in tools_found[:2]:  # 测试前2个工具
                try:
                    tool_func = global_vars[tool_name]
                    print("🧪 测试工具:", tool_name)
                    if 'weather' in tool_name.lower():
                        result = tool_func("Beijing")
                    elif 'calculate' in tool_name.lower():
                        result = tool_func("2+2")
                    else:
                        result = "工具可用"
                    print("🔧 工具输出:", result)
                except Exception as e:
                    print("❌ 工具测试失败:", str(e))

except Exception as e:
    print("❌ 代码执行出错:", str(e))
    import traceback
    traceback.print_exc()

print("-" * 50)
print("📊 执行总结:")
print("总耗时: {:.2f}秒".format(time.time() - execution_start))
print("\\n=== 测试完成 ===")
'''
        
        return test_script
    
    def _execute_script(self, script: str) -> Dict[str, Any]:
        """执行脚本并返回结果"""
        start_time = time.time()
        
        try:
            # 使用当前Python解释器执行
            result = subprocess.run(
                [sys.executable, '-c', script],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=os.getcwd(),
                env=os.environ.copy()  # 传递所有环境变量
            )
            
            execution_time = time.time() - start_time
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "execution_time": execution_time
            }
            
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": f"执行超时 (>{self.timeout}秒)",
                "return_code": -1,
                "execution_time": self.timeout
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": f"执行错误: {str(e)}",
                "return_code": -1,
                "execution_time": time.time() - start_time
            }
    
    def _detect_api_calls(self, output: str) -> bool:
        """检测是否有API调用"""
        api_indicators = [
            "openai",
            "api.openai.com",
            "HTTP",
            "POST",
            "API",
            "token",
            "request",
            "response",
            "completion"
        ]
        
        output_lower = output.lower()
        return any(indicator in output_lower for indicator in api_indicators)
