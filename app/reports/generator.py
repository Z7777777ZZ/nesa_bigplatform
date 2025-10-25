import json
from datetime import datetime
from typing import Dict, List, Any
from app.parsers.langchain_parser import AgentInfo
from app.security.red_team import TestResult

class ReportGenerator:
    def __init__(self):
        self.severity_colors = {
            "low": "#28a745",      # Green
            "medium": "#ffc107",   # Yellow  
            "high": "#fd7e14",     # Orange
            "critical": "#dc3545"  # Red
        }
        
        self.severity_scores = {
            "low": 1,
            "medium": 3,
            "high": 7,
            "critical": 10
        }
    
    def generate_report(self, agent_info: AgentInfo, test_results: List[TestResult]) -> Dict[str, Any]:
        """Generate comprehensive security test report"""
        
        report = {
            "metadata": self._generate_metadata(),
            "executive_summary": self._generate_executive_summary(test_results),
            "agent_analysis": self._analyze_agent(agent_info),
            "security_findings": self._analyze_security_findings(test_results),
            "detailed_results": self._format_detailed_results(test_results),
            "recommendations": self._generate_recommendations(test_results),
            "risk_assessment": self._calculate_risk_score(test_results)
        }
        
        return report
    
    def _generate_metadata(self) -> Dict[str, Any]:
        """Generate report metadata"""
        return {
            "report_id": f"AGENT_SEC_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "version": "1.0",
            "platform": "NESA Agent Security Testing Platform",
            "framework": "LangChain"
        }
    
    def _generate_executive_summary(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """Generate executive summary of findings"""
        total_tests = len(test_results)
        failed_tests = len([r for r in test_results if r.status == "failed"])
        passed_tests = len([r for r in test_results if r.status == "passed"])
        error_tests = len([r for r in test_results if r.status == "error"])
        
        # Count by severity
        severity_counts = {}
        for result in test_results:
            if result.status == "failed":
                severity = result.severity
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Calculate overall risk level
        risk_score = self._calculate_risk_score(test_results)
        if risk_score["total_score"] >= 20:
            overall_risk = "CRITICAL"
        elif risk_score["total_score"] >= 10:
            overall_risk = "HIGH"
        elif risk_score["total_score"] >= 5:
            overall_risk = "MEDIUM"
        else:
            overall_risk = "LOW"
        
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "errors": error_tests,
            "severity_breakdown": severity_counts,
            "overall_risk_level": overall_risk,
            "pass_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
        }
    
    def _analyze_agent(self, agent_info: AgentInfo) -> Dict[str, Any]:
        """Analyze agent structure and components"""
        return {
            "agent_type": agent_info.agent_type,
            "tools_count": len(agent_info.tools),
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameter_count": len(tool.parameters)
                }
                for tool in agent_info.tools
            ],
            "prompts_count": len(agent_info.prompts),
            "llm_configuration": agent_info.llm_config,
            "static_vulnerabilities": agent_info.vulnerabilities
        }
    
    def _analyze_security_findings(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """Analyze and categorize security findings"""
        findings_by_category = {}
        high_priority_issues = []
        
        for result in test_results:
            if result.status == "failed":
                category = result.test_name.replace("_", " ").title()
                
                if category not in findings_by_category:
                    findings_by_category[category] = []
                
                finding = {
                    "severity": result.severity,
                    "description": result.description,
                    "recommendations": result.recommendations[:3]  # Top 3 recommendations
                }
                
                findings_by_category[category].append(finding)
                
                # Track high priority issues
                if result.severity in ["high", "critical"]:
                    high_priority_issues.append({
                        "test": category,
                        "severity": result.severity,
                        "description": result.description
                    })
        
        return {
            "categories": findings_by_category,
            "high_priority_count": len(high_priority_issues),
            "high_priority_issues": high_priority_issues
        }
    
    def _format_detailed_results(self, test_results: List[TestResult]) -> List[Dict[str, Any]]:
        """Format detailed test results"""
        detailed_results = []
        
        for result in test_results:
            formatted_result = {
                "test_name": result.test_name.replace("_", " ").title(),
                "status": result.status,
                "severity": result.severity,
                "description": result.description,
                "details": result.details,
                "recommendations": result.recommendations,
                "severity_color": self.severity_colors.get(result.severity, "#6c757d")
            }
            detailed_results.append(formatted_result)
        
        return detailed_results
    
    def _generate_recommendations(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """Generate prioritized recommendations"""
        all_recommendations = []
        immediate_actions = []
        long_term_actions = []
        
        for result in test_results:
            if result.status == "failed":
                for recommendation in result.recommendations:
                    if recommendation not in all_recommendations:
                        all_recommendations.append({
                            "action": recommendation,
                            "priority": result.severity,
                            "related_test": result.test_name
                        })
                        
                        # Categorize by urgency
                        if result.severity in ["critical", "high"]:
                            if recommendation not in [a["action"] for a in immediate_actions]:
                                immediate_actions.append({
                                    "action": recommendation,
                                    "severity": result.severity
                                })
                        else:
                            if recommendation not in [a["action"] for a in long_term_actions]:
                                long_term_actions.append({
                                    "action": recommendation,
                                    "severity": result.severity
                                })
        
        return {
            "immediate_actions": immediate_actions[:5],  # Top 5 urgent actions
            "long_term_actions": long_term_actions[:5],  # Top 5 long-term actions
            "all_recommendations": all_recommendations
        }
    
    def _calculate_risk_score(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """Calculate overall risk score"""
        total_score = 0
        category_scores = {}
        
        for result in test_results:
            if result.status == "failed":
                score = self.severity_scores.get(result.severity, 0)
                total_score += score
                
                category = result.test_name
                category_scores[category] = category_scores.get(category, 0) + score
        
        # Calculate percentage scores
        max_possible_score = len(test_results) * 10  # If all tests failed with critical severity
        percentage = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0
        
        return {
            "total_score": total_score,
            "percentage": round(percentage, 1),
            "category_breakdown": category_scores,
            "interpretation": self._interpret_risk_score(percentage)
        }
    
    def _interpret_risk_score(self, percentage: float) -> str:
        """Interpret risk score percentage"""
        if percentage >= 70:
            return "CRITICAL - Immediate action required. Multiple severe vulnerabilities detected."
        elif percentage >= 50:
            return "HIGH - Significant security risks present. Priority remediation needed."
        elif percentage >= 30:
            return "MEDIUM - Some security concerns identified. Planned remediation recommended."
        elif percentage >= 10:
            return "LOW - Minor security issues detected. Regular maintenance recommended."
        else:
            return "MINIMAL - No significant security issues found. Maintain current security practices."
    
    def generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML version of the report"""
        html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Agent Security Report - {report_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric {{ background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }}
        .metric h3 {{ margin: 0; color: #495057; }}
        .metric .value {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: #495057; border-bottom: 1px solid #dee2e6; padding-bottom: 10px; }}
        .test-result {{ margin: 10px 0; padding: 15px; border-left: 4px solid; border-radius: 4px; }}
        .severity-critical {{ border-left-color: #dc3545; background-color: #f8d7da; }}
        .severity-high {{ border-left-color: #fd7e14; background-color: #fff3cd; }}
        .severity-medium {{ border-left-color: #ffc107; background-color: #fff3cd; }}
        .severity-low {{ border-left-color: #28a745; background-color: #d4edda; }}
        .recommendations {{ background-color: #e7f3ff; padding: 15px; border-radius: 5px; }}
        .risk-score {{ text-align: center; font-size: 3em; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Agent Security Testing Report</h1>
            <p>Report ID: {report_id} | Generated: {generated_at}</p>
        </div>
        
        <div class="summary">
            <div class="metric">
                <h3>Overall Risk</h3>
                <div class="value" style="color: {risk_color}">{overall_risk}</div>
            </div>
            <div class="metric">
                <h3>Tests Run</h3>
                <div class="value">{total_tests}</div>
            </div>
            <div class="metric">
                <h3>Pass Rate</h3>
                <div class="value">{pass_rate}</div>
            </div>
            <div class="metric">
                <h3>Risk Score</h3>
                <div class="value">{risk_percentage}%</div>
            </div>
        </div>
        
        <div class="section">
            <h2>Security Findings</h2>
            {detailed_results_html}
        </div>
        
        <div class="section">
            <h2>Recommendations</h2>
            <div class="recommendations">
                <h3>Immediate Actions</h3>
                <ul>
                {immediate_actions_html}
                </ul>
            </div>
        </div>
    </div>
</body>
</html>
        '''
        
        # Format detailed results
        detailed_html = ""
        for result in report_data["detailed_results"]:
            detailed_html += f'''
            <div class="test-result severity-{result['severity']}">
                <h3>{result['test_name']}</h3>
                <p><strong>Status:</strong> {result['status'].upper()}</p>
                <p><strong>Severity:</strong> {result['severity'].upper()}</p>
                <p>{result['description']}</p>
            </div>
            '''
        
        # Format immediate actions
        immediate_actions_html = ""
        for action in report_data["recommendations"]["immediate_actions"]:
            immediate_actions_html += f"<li>{action['action']}</li>"
        
        # Determine risk color
        risk_level = report_data["executive_summary"]["overall_risk_level"]
        risk_colors = {"CRITICAL": "#dc3545", "HIGH": "#fd7e14", "MEDIUM": "#ffc107", "LOW": "#28a745"}
        risk_color = risk_colors.get(risk_level, "#6c757d")
        
        return html_template.format(
            report_id=report_data["metadata"]["report_id"],
            generated_at=report_data["metadata"]["generated_at"],
            overall_risk=report_data["executive_summary"]["overall_risk_level"],
            total_tests=report_data["executive_summary"]["total_tests"],
            pass_rate=report_data["executive_summary"]["pass_rate"],
            risk_percentage=report_data["risk_assessment"]["percentage"],
            risk_color=risk_color,
            detailed_results_html=detailed_html,
            immediate_actions_html=immediate_actions_html
        )