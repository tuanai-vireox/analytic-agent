"""
Crew Manager for orchestrating CrewAI agents and tasks.
"""

import asyncio
import uuid
from typing import Dict, Any, Optional
from crewai import Crew, Task
from langchain_openai import ChatOpenAI

from app.config import settings
from app.agents.data_analyst_agent import DataAnalystAgent
from app.agents.researcher_agent import ResearcherAgent
from app.agents.reporter_agent import ReporterAgent


class CrewManager:
    """Manages CrewAI crews and orchestrates analysis tasks."""
    
    def __init__(self):
        """Initialize the Crew Manager."""
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens,
            api_key=settings.openai_api_key
        )
        
        # Initialize agents
        self.researcher_agent = ResearcherAgent().get_agent()
        self.analyst_agent = DataAnalystAgent().get_agent()
        self.reporter_agent = ReporterAgent().get_agent()
    
    async def run_analysis(self, query: str, analysis_type: str, data_source: Optional[str] = None, 
                          parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run a complete analysis using the crew of agents.
        
        Args:
            query: The analysis query
            analysis_type: Type of analysis to perform
            data_source: Optional data source
            parameters: Optional analysis parameters
            
        Returns:
            Analysis results
        """
        try:
            # Create tasks for each agent
            research_task = Task(
                description=self.researcher_agent.research_data_sources(query, f"Analysis type: {analysis_type}"),
                agent=self.researcher_agent,
                expected_output="Comprehensive research findings with data sources and quality assessment"
            )
            
            analysis_task = Task(
                description=self.analyst_agent.analyze_data(
                    data_source or "identified data sources", 
                    analysis_type, 
                    query
                ),
                agent=self.analyst_agent,
                expected_output="Detailed analysis results with insights and patterns",
                context=[research_task]
            )
            
            report_task = Task(
                description=self.reporter_agent.create_report(
                    "analysis results from previous task",
                    query
                ),
                agent=self.reporter_agent,
                expected_output="Comprehensive report with executive summary, findings, and recommendations",
                context=[analysis_task]
            )
            
            # Create and run the crew
            crew = Crew(
                agents=[self.researcher_agent, self.analyst_agent, self.reporter_agent],
                tasks=[research_task, analysis_task, report_task],
                verbose=settings.crewai_verbose,
                memory=settings.crewai_memory,
                max_iter=settings.crewai_max_iterations
            )
            
            # Execute the crew
            result = await asyncio.to_thread(crew.kickoff)
            
            return {
                "task_id": str(uuid.uuid4()),
                "status": "completed",
                "result": result,
                "agents_used": ["researcher", "analyst", "reporter"],
                "iterations_count": 1
            }
            
        except Exception as e:
            return {
                "task_id": str(uuid.uuid4()),
                "status": "failed",
                "error_message": str(e),
                "agents_used": [],
                "iterations_count": 0
            }
    
    def create_simple_analysis(self, query: str, analysis_type: str) -> Dict[str, Any]:
        """
        Create a simple analysis task without full crew execution.
        
        Args:
            query: The analysis query
            analysis_type: Type of analysis to perform
            
        Returns:
            Task information
        """
        return {
            "task_id": str(uuid.uuid4()),
            "query": query,
            "analysis_type": analysis_type,
            "status": "pending",
            "created_at": "2023-12-01T10:00:00Z"
        } 