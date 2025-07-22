"""
Security Analyst (SA) Orchestrator Agent
Coordinates all analysis agents and manages the overall workflow.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

from core.agents.base import BaseAnalysisAgent, AnalysisContext
from core.agents.specialized.suggester import PluginSuggester
from core.memory.context_manager import ContextManager
from core.models.schemas import AnalysisRequest, AnalysisResult
from api.websocket import WebSocketManager


class SecurityAnalystAgent:
    """
    Main orchestrator that:
    1. Manages analysis workflow
    2. Coordinates between agents
    3. Handles chat interactions
    4. Suggests additional analyses
    5. Manages real-time updates
    """
    
    def __init__(
        self,
        analysis_agents: Dict[str, BaseAnalysisAgent],
        plugin_suggester: PluginSuggester,
        context_manager: ContextManager,
        websocket_manager: WebSocketManager
    ):
        self.agents = analysis_agents
        self.suggester = plugin_suggester
        self.context = context_manager
        self.ws_manager = websocket_manager
        
    async def start_analysis(
        self,
        request: AnalysisRequest,
        analysis_id: str
    ) -> AnalysisResult:
        """
        Start full analysis workflow.
        
        IMPORTANT: This runs analyses in dependency order:
        1. STPA-Sec first (defines system structure)
        2. Other analyses use STPA-Sec results
        3. Integration analyses run last
        """
        # Initialize context
        context = AnalysisContext(
            system_description=request.system_description,
            analysis_request=request.dict(),
            enabled_plugins=request.enabled_plugins
        )
        
        # Determine execution order
        execution_order = self._determine_execution_order(
            request.enabled_plugins
        )
        
        # Execute analyses
        results = {}
        for plugin_id in execution_order:
            if plugin_id not in self.agents:
                continue
                
            # Update context with previous results
            context.previous_results = results
            
            # Send real-time update
            await self._send_update(
                analysis_id,
                plugin_id,
                "started"
            )
            
            try:
                # Run analysis
                agent = self.agents[plugin_id]
                result = await agent.analyze(context)
                results[plugin_id] = result
                
                # Store in context manager for future reference
                await self.context.store_result(
                    analysis_id,
                    plugin_id,
                    result
                )
                
                # Send completion update
                await self._send_update(
                    analysis_id,
                    plugin_id,
                    "completed",
                    result
                )
                
            except Exception as e:
                # Handle errors gracefully
                await self._send_update(
                    analysis_id,
                    plugin_id,
                    "error",
                    {"error": str(e)}
                )
                
        # Get suggestions for additional analyses
        suggestions = await self.suggester.suggest_plugins(
            enabled_plugins=request.enabled_plugins,
            analysis_results=results
        )
        
        # Return complete results
        return AnalysisResult(
            analysis_id=analysis_id,
            results=results,
            suggestions=suggestions,
            completed_at=datetime.utcnow()
        )
        
    async def rerun_section(
        self,
        analysis_id: str,
        plugin_id: str,
        section_id: str,
        user_modifications: Optional[str] = None
    ) -> Any:
        """Rerun a specific section with optional modifications"""
        # Get original context
        context = await self.context.get_context(analysis_id)
        
        # Add user modifications
        if user_modifications:
            context.user_modifications = user_modifications
            
        # Get agent and rerun section
        agent = self.agents[plugin_id]
        result = await agent.analyze_section(section_id, context)
        
        # Update stored results
        await self.context.update_section(
            analysis_id,
            plugin_id,
            section_id,
            result
        )
        
        return result
        
    async def chat_query(
        self,
        analysis_id: str,
        query: str
    ) -> str:
        """
        Handle chat queries about the analysis.
        Uses RAG over stored artifacts.
        """
        # Get relevant context
        relevant_artifacts = await self.context.search_artifacts(
            analysis_id,
            query
        )
        
        # Generate response
        # TODO: Implement chat response generation
        pass
        
    def _determine_execution_order(
        self,
        enabled_plugins: List[str]
    ) -> List[str]:
        """
        Determine optimal execution order.
        STPA-Sec should run first as it defines system structure.
        """
        order = []
        
        # STPA-Sec first if enabled
        if "stpa-sec" in enabled_plugins:
            order.append("stpa-sec")
            
        # Other primary analyses
        primary = ["stride", "pasta", "dread", "maestro", 
                  "linddun", "hazop", "octave"]
        for p in primary:
            if p in enabled_plugins and p not in order:
                order.append(p)
                
        # Integration analyses last
        # (These would be added based on what's enabled)
        
        return order
        
    async def _send_update(
        self,
        analysis_id: str,
        plugin_id: str,
        status: str,
        data: Any = None
    ):
        """Send real-time update via WebSocket"""
        await self.ws_manager.send_update(
            analysis_id,
            {
                "type": "analysis_update",
                "plugin": plugin_id,
                "status": status,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
        )