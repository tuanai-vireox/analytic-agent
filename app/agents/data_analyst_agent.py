"""
Data Analyst Agent for performing data analysis tasks.
"""

from crewai import Agent
from langchain_openai import ChatOpenAI
from app.config import settings


class DataAnalystAgent:
    """Data Analyst Agent specialized in data analysis and statistical modeling."""
    
    def __init__(self):
        """Initialize the Data Analyst Agent."""
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens,
            api_key=settings.openai_api_key
        )
        
        self.agent = Agent(
            role="Data Analyst",
            goal="Perform comprehensive data analysis to extract meaningful insights and patterns",
            backstory="""You are an expert data analyst with years of experience in statistical analysis, 
            data visualization, and business intelligence. You excel at identifying trends, patterns, 
            and anomalies in data, and can provide actionable insights to drive business decisions.""",
            verbose=settings.crewai_verbose,
            allow_delegation=False,
            llm=self.llm,
            tools=[]  # Add specific tools as needed
        )
    
    def get_agent(self) -> Agent:
        """Get the configured agent instance."""
        return self.agent
    
    def analyze_data(self, data_source: str, analysis_type: str, query: str) -> str:
        """
        Perform data analysis based on the given parameters.
        
        Args:
            data_source: Source of the data to analyze
            analysis_type: Type of analysis to perform
            query: Specific query or question to answer
            
        Returns:
            Analysis results as a string
        """
        task_description = f"""
        Analyze the data from {data_source} to answer: {query}
        
        Analysis Type: {analysis_type}
        
        Please provide:
        1. Summary of findings
        2. Key insights and patterns
        3. Statistical analysis
        4. Visualizations (if applicable)
        5. Recommendations based on the data
        """
        
        # This would be executed by the crew manager
        return task_description 