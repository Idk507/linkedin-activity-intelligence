# Define the state schema for LangGraph
class LAIEState(TypedDict):
    """State schema for the LAIE multi-agent system."""
    # Input parameters
    public_id: str
    data_sources: Dict[str, Any]
    
    # Data collection results
    raw_profile: Optional[Dict[str, Any]]
    raw_posts: Optional[List[Dict[str, Any]]]
    data_quality_score: float
    
    # Analytics results
    monthly_analytics: Optional[List[Dict[str, Any]]]
    content_performance: Optional[Dict[str, Any]]
    temporal_patterns: Optional[Dict[str, Any]]
    
    # AI-generated content
    monthly_notes: Optional[List[Dict[str, Any]]]
    executive_summary: Optional[str]
    recommendations: Optional[List[str]]
    
    # Agent communication
    messages: List[BaseMessage]
    current_agent: str
    next_agent: Optional[str]
    
    # Error handling
    errors: List[str]
    retry_count: int
    
    # Final output
    final_report: Optional[Dict[str, Any]]
    audit_trail: List[Dict[str, Any]]


# define agent response types 
class AgentResponse(TypedDict):
    success : bool 
    data : Any 
    next_agent : Optional[str]
    errors : List[str]



# Define monthly note structure
class MonthlyNote(TypedDict):
    month: str
    activity_summary: str
    key_achievements: List[str]
    content_performance: Dict[str, Any]
    engagement_highlights: List[str]
    recommendations: List[str]
    ai_insights: str
