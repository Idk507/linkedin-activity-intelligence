# Define the LangGraph workflow
def ingestion_node(state: LAIEState) -> LAIEState:
    """Ingestion agent node."""
    response = ingestion_agent.process(state)
    
    if response["success"]:
        data = response["data"]
        return {
            **state,
            "raw_profile": data["profile"],
            "raw_posts": data["posts"],
            "data_quality_score": data["quality_score"],
            "current_agent": "analytics",
            "next_agent": response["next_agent"],
            "messages": state["messages"] + [AIMessage(content=response["message"])],
            "audit_trail": state["audit_trail"] + [{
                "agent": "ingestion",
                "action": "data_collection",
                "timestamp": datetime.utcnow().isoformat(),
                "success": True
            }]
        }
    else:
        return {
            **state,
            "errors": state["errors"] + response["errors"],
            "messages": state["messages"] + [AIMessage(content=f"Ingestion failed: {response['message']}")],
            "audit_trail": state["audit_trail"] + [{
                "agent": "ingestion",
                "action": "data_collection",
                "timestamp": datetime.utcnow().isoformat(),
                "success": False,
                "error": response["message"]
            }]
        }



def analytics_node(state: LAIEState) -> LAIEState:
    """Analytics agent node."""
    response = analytics_agent.process(state)
    
    if response["success"]:
        data = response["data"]
        return {
            **state,
            "monthly_analytics": data["monthly_analytics"],
            "content_performance": data["content_performance"],
            "temporal_patterns": data["temporal_patterns"],
            "current_agent": "monthly_analysis",
            "next_agent": response["next_agent"],
            "messages": state["messages"] + [AIMessage(content=response["message"])],
            "audit_trail": state["audit_trail"] + [{
                "agent": "analytics",
                "action": "analytics_computation",
                "timestamp": datetime.utcnow().isoformat(),
                "success": True
            }]
        }
    else:
        return {
            **state,
            "errors": state["errors"] + response["errors"],
            "messages": state["messages"] + [AIMessage(content=f"Analytics failed: {response['message']}")],
            "audit_trail": state["audit_trail"] + [{
                "agent": "analytics",
                "action": "analytics_computation",
                "timestamp": datetime.utcnow().isoformat(),
                "success": False,
                "error": response["message"]
            }]
        }



def monthly_analysis_node(state: LAIEState) -> LAIEState:
    """Monthly analysis agent node."""
    response = monthly_analysis_agent.process(state)
    
    if response["success"]:
        return {
            **state,
            "monthly_notes": response["data"],
            "current_agent": "summary",
            "next_agent": response["next_agent"],
            "messages": state["messages"] + [AIMessage(content=response["message"])],
            "audit_trail": state["audit_trail"] + [{
                "agent": "monthly_analysis",
                "action": "monthly_notes_generation",
                "timestamp": datetime.utcnow().isoformat(),
                "success": True
            }]
        }
    else:
        return {
            **state,
            "errors": state["errors"] + response["errors"],
            "messages": state["messages"] + [AIMessage(content=f"Monthly analysis failed: {response['message']}")],
            "audit_trail": state["audit_trail"] + [{
                "agent": "monthly_analysis",
                "action": "monthly_notes_generation",
                "timestamp": datetime.utcnow().isoformat(),
                "success": False,
                "error": response["message"]
            }]
        }




def summary_node(state: LAIEState) -> LAIEState:
    """Summary agent node."""
    response = summary_agent.process(state)
    
    if response["success"]:
        data = response["data"]
        return {
            **state,
            "executive_summary": data["executive_summary"],
            "recommendations": data["recommendations"],
            "final_report": data["final_report"],
            "current_agent": "complete",
            "next_agent": None,
            "messages": state["messages"] + [AIMessage(content=response["message"])],
            "audit_trail": state["audit_trail"] + [{
                "agent": "summary",
                "action": "final_report_generation",
                "timestamp": datetime.utcnow().isoformat(),
                "success": True
            }]
        }
    else:
        return {
            **state,
            "errors": state["errors"] + response["errors"],
            "messages": state["messages"] + [AIMessage(content=f"Summary failed: {response['message']}")],
            "audit_trail": state["audit_trail"] + [{
                "agent": "summary",
                "action": "final_report_generation",
                "timestamp": datetime.utcnow().isoformat(),
                "success": False,
                "error": response["message"]
            }]
        }



def route_based_on_success(state: LAIEState) -> str:
    """Route to next agent or handle errors."""
    if state["errors"] and len(state["errors"]) > 0 and state["retry_count"] >= 3:
        return "error_handler"
    
    next_agent = state.get("next_agent")
    if next_agent == "analytics":
        return "analytics"
    elif next_agent == "monthly_analysis":
        return "monthly_analysis"
    elif next_agent == "summary":
        return "summary"
    else:
        return "end"


def error_handler_node(state: LAIEState) -> LAIEState:
    """Handle errors and create fallback report."""
    logger.error("Workflow failed with errors", errors=state["errors"])
    
    # Create minimal fallback report
    fallback_report = {
        "error_report": True,
        "errors": state["errors"],
        "partial_data": {
            "profile": state.get("raw_profile"),
            "monthly_analytics": state.get("monthly_analytics", [])
        },
        "recommendation": "Please check data sources and try again"
    }
    
    return {
        **state,
        "final_report": fallback_report,
        "messages": state["messages"] + [AIMessage(content="Workflow completed with errors - see final_report for details")]
    }
