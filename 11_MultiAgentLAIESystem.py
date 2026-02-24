class MultiAgentLAIESystem:
    """Main orchestrator for the Multi-Agent LAIE system using LangGraph."""
    
    def __init__(self):
        self.graph = laie_graph
        self.audit_log = []
        logger.info("MultiAgentLAIESystem initialized")
    
    def run_analysis(self, public_id: str, data_sources: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the complete multi-agent LAIE analysis.
        
        Args:
            public_id: LinkedIn public profile identifier
            data_sources: Dictionary of available data sources
        
        Returns:
            Complete analysis results
        """
        # FIX: Remove logger.info with keyword argument
        logger.info(f"Starting multi-agent LAIE analysis for public_id={public_id}")
        
        # Prepare initial state
        initial_state = LAIEState(
            public_id=public_id,
            data_sources=data_sources or {},
            messages=[HumanMessage(content=f"Analyze LinkedIn activity for {public_id}")],
            current_agent="ingestion",
            errors=[],
            retry_count=0,
            audit_trail=[]
        )
        
        try:
            # Execute the LangGraph workflow
            print(f"\n Starting Multi-Agent LAIE Analysis for {public_id}")
            print("=" * 60)
            
            result_state = self.graph.invoke(initial_state)
            
            # Process results
            success = len(result_state.get("errors", [])) == 0
            final_report = result_state.get("final_report")
            
            result = {
                "success": success,
                "public_id": public_id,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "data_quality_score": result_state.get("data_quality_score", 0.0),
                "agent_workflow": {
                    "total_agents": 4,
                    "agents_executed": len(result_state.get("audit_trail", [])),
                    "final_agent": result_state.get("current_agent", "unknown")
                },
                "results": {
                    "profile": result_state.get("raw_profile"),
                    "monthly_analytics": result_state.get("monthly_analytics", []),
                    "monthly_notes": result_state.get("monthly_notes", []),
                    "executive_summary": result_state.get("executive_summary", ""),
                    "recommendations": result_state.get("recommendations", []),
                    "final_report": final_report
                } if success else None,
                "errors": result_state.get("errors", []),
                "audit_trail": result_state.get("audit_trail", []),
                "agent_messages": [msg.content for msg in result_state.get("messages", [])]
            }
            
            if success:
                print("\n Multi-Agent Analysis Completed Successfully!")
                print(f" Data Quality Score: {result['data_quality_score']:.1%}")
                print(f" Monthly Notes Generated: {len(result['results']['monthly_notes'])}")
                print(f" Recommendations: {len(result['results']['recommendations'])}")
            else:
                print("\n Analysis Completed with Errors")
                print(f" Errors: {len(result['errors'])}")
            
            self._log_completion(success, public_id)
            return result
            
        except Exception as e:
            logger.error("Multi-agent analysis failed", error=str(e))
            return {
                "success": False,
                "public_id": public_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status and agent states."""
        return {
            "system_status": "active",
            "agents": {
                "ingestion": "ready",
                "analytics": "ready",
                "monthly_analysis": "ready",
                "summary": "ready"
            },
            "langgraph_compiled": True,
            "last_audit_entries": self.audit_log[-5:] if self.audit_log else []
        }
    
    def _log_completion(self, success: bool, public_id: str):
        """Log analysis completion."""
        status = "success" if success else "failed"
        timestamp = datetime.utcnow().isoformat()
        self.audit_log.append({
            "timestamp": timestamp,
            "action": f"analysis_completed_{status}",
            "public_id": public_id,
            "status": status
        })
