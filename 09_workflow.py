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
