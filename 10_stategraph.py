# create the langGraph workflow

workflow = StateGraph(LAIEState)



# Add nodes
workflow.add_node("ingestion", ingestion_node)
workflow.add_node("analytics", analytics_node)
workflow.add_node("monthly_analysis", monthly_analysis_node)
workflow.add_node("summary", summary_node)
workflow.add_node("error_handler", error_handler_node)

# Add edges
workflow.add_edge("ingestion", "analytics")
workflow.add_edge("analytics", "monthly_analysis")
workflow.add_edge("monthly_analysis", "summary")
workflow.add_edge("summary", END)
workflow.add_edge("error_handler", END)

# Add conditional edges
workflow.add_conditional_edges(
    "analytics",
    route_based_on_success,
    {
        "monthly_analysis": "monthly_analysis",
        "error_handler": "error_handler",
        "end": END
    }
)


workflow.add_conditional_edges(
    "monthly_analysis",
    route_based_on_success,
    {
        "summary": "summary",
        "error_handler": "error_handler",
        "end": END
    }
)


# Set entry point
workflow.set_entry_point("ingestion")




# Compile the workflow
laie_graph = workflow.compile()


print("   → 4 agent nodes: ingestion → analytics → monthly_analysis → summary")
print("   → Conditional routing based on success/failure")
print("   → Error handling and recovery")
print("   → Complete state management")

from IPython.display import Image, display


# visualize the workflow

graph_img = laie_graph.get_graph()
