import subprocess
import tempfile
import os
import signal
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    return_code: int
    execution_time: float
    timeout: bool
    error_message: Optional[str] = None

class SandboxExecutor:
    def __init__(self, timeout: int = 30, memory_limit: str = "128M"):
        self.timeout = timeout
        self.memory_limit = memory_limit
        self.restricted_imports = [
            'subprocess', 'os', 'sys', 'shutil', 'glob',
            'socket', 'urllib', 'requests', 'http',
            'ftplib', 'smtplib', 'telnetlib'
        ]
    
    def execute_agent(self, file_path: str, input_data: str = "") -> ExecutionResult:
        """Execute agent in a sandboxed environment"""
        start_time = time.time()
        
        try:
            # Read the original file
            with open(file_path, 'r') as f:
                original_code = f.read()
            
            # Create sandboxed version
            sandboxed_code = self._create_sandboxed_code(original_code, input_data)
            
            # Execute in temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(sandboxed_code)
                temp_file.flush()
                
                try:
                    result = self._execute_with_limits(temp_file.name)
                    result.execution_time = time.time() - start_time
                    return result
                finally:
                    os.unlink(temp_file.name)
                    
        except Exception as e:
            return ExecutionResult(
                stdout="",
                stderr=f"Sandbox setup error: {str(e)}",
                return_code=-1,
                execution_time=time.time() - start_time,
                timeout=False,
                error_message=str(e)
            )
    
    def _create_sandboxed_code(self, original_code: str, input_data: str) -> str:
        """Create a sandboxed version of the code with restricted imports and mocked functions"""
        
        sandbox_header = '''
import sys
import io
import os
from unittest.mock import Mock, patch

# Set environment variables for the agent
os.environ['OPENAI_API_KEY'] = "{api_key}"
os.environ['OPENAI_BASE_URL'] = "{base_url}"

# Capture stdout for analysis
captured_output = io.StringIO()
original_stdout = sys.stdout
sys.stdout = captured_output

# Mock dangerous functions but allow eval for testing purposes
def mock_input(prompt=""):
    return "{input_data}"

# Create a controlled eval that logs but still executes (for testing purposes)
original_eval = eval
def controlled_eval(*args, **kwargs):
    print("SECURITY: eval() called with:", args[0] if args else "unknown")
    try:
        return original_eval(*args, **kwargs)
    except Exception as e:
        print(f"SECURITY: eval() failed: {{e}}")
        return f"Error: {{e}}"

def mock_exec(*args, **kwargs):
    print("SECURITY: exec() call blocked")
    return None

# Mock only dangerous network/system operations
original_import = __import__
def safe_import(name, *args, **kwargs):
    # Block dangerous modules but allow AI/ML libraries
    blocked_modules = ['subprocess', 'os.system', 'socket', 'telnetlib', 'ftplib', 'smtplib']
    if name in blocked_modules:
        print(f"SECURITY: Import of {{name}} blocked")
        return Mock()
    return original_import(name, *args, **kwargs)

# Apply security patches
import builtins
builtins.input = mock_input
builtins.eval = controlled_eval
builtins.exec = mock_exec
builtins.__import__ = safe_import

# Mock only dangerous os functions, not the whole module
import os
original_system = getattr(os, 'system', None)
original_popen = getattr(os, 'popen', None)

def mock_system(*args):
    print("SECURITY: os.system() call blocked")
    return 0

def mock_popen(*args):
    print("SECURITY: os.popen() call blocked")
    return Mock()

if original_system:
    os.system = mock_system
if original_popen:
    os.popen = mock_popen

try:
'''.format(
            input_data=input_data.replace('"', '\\"'),
            api_key=os.getenv('OPENAI_API_KEY', ''),
            base_url=os.getenv('OPENAI_BASE_URL', '')
        )
        
        sandbox_footer = '''
except Exception as e:
    print(f"Execution error: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Print captured output
    sys.stdout = original_stdout
    print("SANDBOX_OUTPUT_START")
    print(captured_output.getvalue())
    print("SANDBOX_OUTPUT_END")
'''
        
        # Indent the original code
        indented_code = '\n'.join('    ' + line for line in original_code.split('\n'))
        
        return sandbox_header + indented_code + sandbox_footer
    
    def _execute_with_limits(self, file_path: str) -> ExecutionResult:
        """Execute Python file with resource limits"""
        try:
            # Use the same Python interpreter that's running this script
            import sys as current_sys
            python_executable = current_sys.executable
            
            # Create the command with resource limits
            cmd = [
                python_executable,
                '-c',
                f'''
import resource
import signal
import sys
import os

# Add current directory to Python path to find modules
sys.path.insert(0, os.getcwd())

# Set memory limit (more generous for ML libraries)
try:
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))  # 512MB
except:
    pass

# Set timeout handler
def timeout_handler(signum, frame):
    raise TimeoutError("Execution timeout")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm({self.timeout})

# Execute the file
try:
    with open(r"{file_path}", 'r', encoding='utf-8') as f:
        code = f.read()
    exec(code)
except TimeoutError:
    print("TIMEOUT_ERROR", file=sys.stderr)
    sys.exit(124)
except Exception as e:
    print(f"EXECUTION_ERROR: {{e}}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
'''
            ]
            
            # Execute with timeout
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid  # Create new process group
            )
            
            try:
                stdout, stderr = process.communicate(timeout=self.timeout + 5)
                return_code = process.returncode
                timeout_occurred = False
                
            except subprocess.TimeoutExpired:
                # Kill the entire process group
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                stdout, stderr = process.communicate()
                return_code = -1
                timeout_occurred = True
                stderr += "\nExecution timeout exceeded"
            
            return ExecutionResult(
                stdout=stdout,
                stderr=stderr,
                return_code=return_code,
                execution_time=0,  # Will be set by caller
                timeout=timeout_occurred
            )
            
        except Exception as e:
            return ExecutionResult(
                stdout="",
                stderr=f"Execution setup error: {str(e)}",
                return_code=-1,
                execution_time=0,
                timeout=False,
                error_message=str(e)
            )
    
    def analyze_execution_safety(self, result: ExecutionResult) -> Dict[str, Any]:
        """Analyze execution result for security indicators"""
        analysis = {
            "blocked_operations": [],
            "security_violations": [],
            "output_analysis": {},
            "risk_level": "low"
        }
        
        # Check for blocked operations
        if "SECURITY:" in result.stdout:
            blocked_ops = [line for line in result.stdout.split('\n') if 'SECURITY:' in line]
            analysis["blocked_operations"] = blocked_ops
            analysis["risk_level"] = "medium"
        
        # Check for timeout (potential DoS)
        if result.timeout:
            analysis["security_violations"].append("Execution timeout - potential DoS")
            analysis["risk_level"] = "high"
        
        # Check for suspicious output patterns
        suspicious_patterns = [
            "HACKED", "INJECTED", "VULNERABLE", "SECRET", "API_KEY",
            "system prompt", "configuration", "override"
        ]
        
        output_text = result.stdout.lower()
        for pattern in suspicious_patterns:
            if pattern.lower() in output_text:
                analysis["security_violations"].append(f"Suspicious output detected: {pattern}")
                analysis["risk_level"] = "high"
        
        # Analyze error patterns
        if "PermissionError" in result.stderr:
            analysis["blocked_operations"].append("File access violation blocked")
        
        return analysis