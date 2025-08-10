"""
Researcher Agent for gathering and validating data sources.
"""

from crewai import Agent
from langchain_openai import ChatOpenAI
from app.config import settings


class ResearcherAgent:
    """Researcher Agent specialized in data gathering and validation."""
    
    def __init__(self):
        """Initialize the Researcher Agent."""
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens,
            api_key=settings.openai_api_key
        )
        
        self.agent = Agent(
            role="Data Researcher",
            goal="Gather, validate, and prepare data sources for analysis",
            backstory="""You are a skilled data researcher with expertise in data collection, 
            validation, and preparation. You have a keen eye for data quality and can identify 
            the most relevant and reliable data sources for any given analysis task.""",
            verbose=settings.crewai_verbose,
            allow_delegation=False,
            llm=self.llm,
            tools=[]  # Add specific tools as needed
        )
    
    def get_agent(self) -> Agent:
        """Get the configured agent instance."""
        return self.agent
    
    def research_data_sources(self, query: str, data_requirements: str) -> str:
        """
        Research and identify relevant data sources.
        
        Args:
            query: The analysis query
            data_requirements: Specific data requirements
            
        Returns:
            Research results as a string
        """
        task_description = f"""
        Research data sources for the query: {query}
        
        Data Requirements: {data_requirements}
        
        Please provide:
        1. Relevant data sources identified
        2. Data quality assessment
        3. Data accessibility information
        4. Recommended data collection methods
        5. Potential data limitations or gaps
        """
        
        return task_description 