from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import shutil
import os
from typing import List
from dotenv import load_dotenv
from app.parsers.langchain_parser import LangChainParser
from app.security.red_team import RedTeamTester
from app.reports.generator import ReportGenerator

# 加载环境变量
load_dotenv()

app = FastAPI(title="Agent Security Testing Platform")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_agent(
    request: Request,
    file: UploadFile = File(...),
    test_methods: List[str] = Form(...)
):
    # Save uploaded file
    upload_path = f"uploads/{file.filename}"
    file_content = await file.read()
    with open(upload_path, "wb") as buffer:
        buffer.write(file_content)
    
    try:
        # Parse agent
        parser = LangChainParser()
        agent_info = parser.parse_file(upload_path)
        
        # Run security tests
        tester = RedTeamTester()
        test_results = []
        
        for method in test_methods:
            result = tester.run_test(method, agent_info, upload_path)
            test_results.append(result)
        
        # Generate report
        report_gen = ReportGenerator()
        report = report_gen.generate_report(agent_info, test_results)
        
        return JSONResponse({
            "status": "success",
            "report": report,
            "agent_info": agent_info.to_dict(),
            "test_details": {
                "file_name": file.filename,
                "file_size": len(file_content),
                "selected_tests": test_methods,
                "execution_details": {
                    "parsed_successfully": True,
                    "tools_found": len(agent_info.tools),
                    "prompts_found": len(agent_info.prompts),
                    "static_vulnerabilities": len(agent_info.vulnerabilities)
                }
            }
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        })

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("PLATFORM_HOST", "0.0.0.0")
    port = int(os.getenv("PLATFORM_PORT", "8000"))
    debug = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    if debug:
        uvicorn.run("main:app", host=host, port=port, reload=True)
    else:
        uvicorn.run(app, host=host, port=port)