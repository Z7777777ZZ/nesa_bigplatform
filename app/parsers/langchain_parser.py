import ast
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class ToolInfo:
    name: str
    description: str
    function_code: str
    parameters: Dict[str, Any]
    
    def to_dict(self):
        return asdict(self)

@dataclass
class AgentInfo:
    agent_type: str
    tools: List[ToolInfo]
    prompts: List[str]
    llm_config: Dict[str, Any]
    execution_flow: List[str]
    vulnerabilities: List[str]
    
    def to_dict(self):
        return {
            "agent_type": self.agent_type,
            "tools": [tool.to_dict() for tool in self.tools],
            "prompts": self.prompts,
            "llm_config": self.llm_config,
            "execution_flow": self.execution_flow,
            "vulnerabilities": self.vulnerabilities
        }

class LangChainParser:
    def __init__(self):
        self.agent_patterns = {
            'initialize_agent': r'initialize_agent\s*\(',
            'AgentExecutor': r'AgentExecutor\s*\(',
            'create_react_agent': r'create_react_agent\s*\(',
            'create_openai_tools_agent': r'create_openai_tools_agent\s*\('
        }
        
    def parse_file(self, file_path: str) -> AgentInfo:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_code(content)
    
    def parse_code(self, code: str) -> AgentInfo:
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"Invalid Python code: {e}")
        
        agent_info = AgentInfo(
            agent_type="unknown",
            tools=[],
            prompts=[],
            llm_config={},
            execution_flow=[],
            vulnerabilities=[]
        )
        
        # Extract information using AST
        self._extract_agent_type(code, agent_info)
        self._extract_tools(tree, agent_info)
        self._extract_prompts(code, agent_info)
        self._extract_llm_config(tree, agent_info)
        self._analyze_vulnerabilities(code, agent_info)
        
        return agent_info
    
    def _extract_agent_type(self, code: str, agent_info: AgentInfo):
        for agent_type, pattern in self.agent_patterns.items():
            if re.search(pattern, code):
                agent_info.agent_type = agent_type
                break
    
    def _extract_tools(self, tree: ast.AST, agent_info: AgentInfo):
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function has @tool decorator
                if any(self._is_tool_decorator(decorator) for decorator in node.decorator_list):
                    tool_info = ToolInfo(
                        name=node.name,
                        description=self._extract_docstring(node),
                        function_code=ast.unparse(node),
                        parameters=self._extract_function_params(node)
                    )
                    agent_info.tools.append(tool_info)
    
    def _is_tool_decorator(self, decorator) -> bool:
        if isinstance(decorator, ast.Name):
            return decorator.id == 'tool'
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr == 'tool'
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id == 'tool'
            elif isinstance(decorator.func, ast.Attribute):
                return decorator.func.attr == 'tool'
        return False
    
    def _extract_docstring(self, node: ast.FunctionDef) -> str:
        if (node.body and isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            return node.body[0].value.value
        return ""
    
    def _extract_function_params(self, node: ast.FunctionDef) -> Dict[str, Any]:
        params = {}
        for arg in node.args.args:
            params[arg.arg] = {
                "type": "unknown",
                "annotation": ast.unparse(arg.annotation) if arg.annotation else None
            }
        return params
    
    def _extract_prompts(self, code: str, agent_info: AgentInfo):
        # Extract string literals that might be prompts
        prompt_patterns = [
            r'prompt\s*=\s*["\']([^"\']+)["\']',
            r'PromptTemplate\([^)]*template\s*=\s*["\']([^"\']+)["\']',
            r'ChatPromptTemplate\.[^(]*\([^)]*["\']([^"\']+)["\']'
        ]
        
        for pattern in prompt_patterns:
            matches = re.findall(pattern, code, re.DOTALL)
            agent_info.prompts.extend(matches)
    
    def _extract_llm_config(self, tree: ast.AST, agent_info: AgentInfo):
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Look for LLM initialization
                if (isinstance(node.func, ast.Name) and 
                    'llm' in node.func.id.lower()):
                    config = {}
                    for keyword in node.keywords:
                        if isinstance(keyword.value, ast.Constant):
                            config[keyword.arg] = keyword.value.value
                    agent_info.llm_config.update(config)
    
    def _analyze_vulnerabilities(self, code: str, agent_info: AgentInfo):
        vulnerabilities = []
        
        # Check for potential prompt injection vulnerabilities
        if re.search(r'input\(\s*\)|raw_input\(\s*\)', code):
            vulnerabilities.append("Direct user input without sanitization")
        
        if re.search(r'f["\'][^"\']*\{[^}]*\}[^"\']*["\']', code):
            vulnerabilities.append("F-string with user input - potential injection")
        
        if re.search(r'\.format\s*\([^)]*\)', code):
            vulnerabilities.append("String formatting with user input")
        
        if re.search(r'eval\s*\(|exec\s*\(', code):
            vulnerabilities.append("Use of eval/exec - code injection risk")
        
        if re.search(r'subprocess|os\.system|os\.popen', code):
            vulnerabilities.append("System command execution")
        
        agent_info.vulnerabilities = vulnerabilities