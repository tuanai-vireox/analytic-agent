"""
Reporter Agent for generating comprehensive reports and summaries.
"""

from crewai import Agent
from langchain_openai import ChatOpenAI
from app.config import settings


class ReporterAgent:
    """Reporter Agent specialized in creating comprehensive reports and summaries."""
    
    def __init__(self):
        """Initialize the Reporter Agent."""
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens,
            api_key=settings.openai_api_key
        )
        
        self.agent = Agent(
            role="Report Writer",
            goal="Create clear, comprehensive, and actionable reports based on analysis results",
            backstory="""You are an expert report writer with years of experience in business 
            intelligence and data storytelling. You excel at translating complex analysis results 
            into clear, actionable insights that stakeholders can easily understand and act upon.""",
            verbose=settings.crewai_verbose,
            allow_delegation=False,
            llm=self.llm,
            tools=[]  # Add specific tools as needed
        )
    
    def get_agent(self) -> Agent:
        """Get the configured agent instance."""
        return self.agent
    
    def create_report(self, analysis_results: str, query: str, target_audience: str = "business stakeholders") -> str:
        """
        Create a comprehensive report based on analysis results.
        
        Args:
            analysis_results: Results from the analysis
            query: Original query that was analyzed
            target_audience: Target audience for the report
            
        Returns:
            Generated report as a string
        """
        task_description = f"""
        Create a comprehensive report based on the analysis results for the query: {query}
        
        Target Audience: {target_audience}
        
        Analysis Results: {analysis_results}
        
        Please structure the report with:
        1. Executive Summary
        2. Key Findings
        3. Detailed Analysis
        4. Visualizations and Charts
        5. Recommendations
        6. Next Steps
        7. Appendices (if needed)
        
        Make the report clear, actionable, and suitable for the target audience.
        """
        
        return task_description 