class SummaryAgent:
    """Agent responsible for creating comprehensive executive summaries and final reports."""
    
    def __init__(self):
        self.audit_log = []
        logger.info("SummaryAgent initialized")
    
    def process(self, state: LAIEState) -> AgentResponse:
        """Generate comprehensive executive summary and final recommendations."""
        logger.info("SummaryAgent processing")
        
        try:
            monthly_notes = state.get("monthly_notes", [])
            profile_data = state.get("raw_profile", {})
            content_performance = state.get("content_performance", {})
            temporal_patterns = state.get("temporal_patterns", {})
            
            if not monthly_notes:
                raise ValueError("No monthly notes available for summary")
            
            # Generate executive summary
            executive_summary = self._generate_executive_summary(
                monthly_notes, profile_data, content_performance, temporal_patterns
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                monthly_notes, content_performance, temporal_patterns
            )
            
            # Create final report
            final_report = self._create_final_report(
                profile_data, monthly_notes, executive_summary, recommendations
            )
            
            response = AgentResponse(
                success=True,
                data={
                    "executive_summary": executive_summary,
                    "recommendations": recommendations,
                    "final_report": final_report
                },
                message="Executive summary and recommendations generated successfully",
                next_agent=None,  # End of pipeline
                errors=[]
            )
            
            self._log_action("Executive summary and final report completed")
            
        except Exception as e:
            logger.error("SummaryAgent failed", error=str(e))
            response = AgentResponse(
                success=False,
                data=None,
                message=f"Summary generation failed: {str(e)}",
                next_agent=None,
                errors=[str(e)]
            )
        
        return response
    
    def _generate_executive_summary(self, monthly_notes: List[MonthlyNote], 
                                  profile_data: Dict[str, Any],
                                  content_performance: Dict[str, Any],
                                  temporal_patterns: Dict[str, Any]) -> str:
        """Generate comprehensive executive summary using AI."""
        profile_name = profile_data.get("full_name", "Professional")
        total_months = len(monthly_notes)
        
        # Aggregate key metrics
        total_posts = sum(note.get("posts_count", 0) for note in monthly_notes)
        avg_engagement = sum(note.get("engagement_rate", 0) for note in monthly_notes) / total_months if total_months > 0 else 0
        
        # Best performing month
        best_month = max(monthly_notes, key=lambda x: x.get("total_impressions", 0)) if monthly_notes else None
        
        prompt = f"""Create a comprehensive executive summary for {profile_name}'s LinkedIn activity from January 2025 to December 2025.
        
EXECUTIVE SUMMARY REQUIREMENTS:

OVERVIEW
- Total months analyzed: {total_months}
- Total posts: {total_posts}
- Average engagement rate: {avg_engagement:.1%}
- Best performing month: {best_month.get('month') if best_month else 'N/A'}

CONTENT & PERFORMANCE ANALYSIS:
- Content performance data: {content_performance}
- Temporal patterns: {temporal_patterns}

MONTHLY HIGHLIGHTS:
{chr(10).join([f"- {note.get('month', 'Unknown')}: {note.get('activity_summary', '')[:100]}..." for note in monthly_notes[:6]])}

Please structure the executive summary as follows:

1. EXECUTIVE OVERVIEW: 3-4 sentences summarizing overall performance and key achievements

2. PERFORMANCE METRICS: Key quantitative results and trends

3. CONTENT STRATEGY ANALYSIS: Insights about what worked and what didn't

4. AUDIENCE ENGAGEMENT: Analysis of audience behavior and response patterns

5. STRATEGIC INSIGHTS: High-level observations about LinkedIn presence and growth

Keep the summary professional, data-driven, and focused on actionable insights."""
        
        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            logger.warning(f"Executive summary generation failed: {e}")
            return self._create_fallback_summary(profile_name, total_posts, avg_engagement)
    
    def _generate_recommendations(self, monthly_notes: List[MonthlyNote],
                                content_performance: Dict[str, Any],
                                temporal_patterns: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations using AI."""
        
        # Extract performance data
        best_content_type = content_performance.get("best_performing_type", "text")
        posting_consistency = temporal_patterns.get("posting_consistency", 0)
        best_weekday = temporal_patterns.get("best_posting_weekday", "Wednesday")
        best_hour = temporal_patterns.get("best_posting_hour", 9)
        
        prompt = f"""Based on the LinkedIn analytics data, generate 5-7 actionable recommendations for optimizing LinkedIn presence.

PERFORMANCE DATA:
- Best performing content type: {best_content_type}
- Posting consistency: {posting_consistency:.1%}
- Optimal posting day: {best_weekday}
- Optimal posting hour: {best_hour}:00
- Monthly activity patterns: {[note.get('month') + ': ' + str(note.get('posts_count', 0)) + ' posts' for note in monthly_notes]}

Generate specific, actionable recommendations covering:
1. Content strategy optimization
2. Posting schedule optimization
3. Engagement improvement tactics
4. Audience growth strategies
5. Performance measurement approaches

Each recommendation should be:
- Specific and actionable
- Grounded in the performance data
- Measurable where possible
- Realistic to implement

Format as a numbered list of clear, concise recommendations."""
        
        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            recommendations_text = response.content
            
            # Parse into list
            lines = recommendations_text.split('\n')
            recommendations = []
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith(("-", "•"))):
                    # Clean up the recommendation text
                    clean_rec = line.lstrip("123456789-• ")
                    if clean_rec:
                        recommendations.append(clean_rec)
            
            return recommendations[:7]  # Limit to 7 recommendations
            
        except Exception as e:
            logger.warning(f"Recommendations generation failed: {e}")
            return self._create_fallback_recommendations()
    
    def _create_final_report(self, profile_data: Dict[str, Any], 
                           monthly_notes: List[MonthlyNote],
                           executive_summary: str, 
                           recommendations: List[str]) -> Dict[str, Any]:
        """Create the final comprehensive report."""
        return {
            "report_title": f"LinkedIn Activity Intelligence Report - {profile_data.get('full_name', 'Professional')}",
            "analysis_period": {
                "start": ANALYSIS_START_DATE.strftime("%B %Y"),
                "end": ANALYSIS_END_DATE.strftime("%B %Y"),
                "total_months": len(monthly_notes)
            },
            "profile_summary": {
                "name": profile_data.get("full_name", ""),
                "headline": profile_data.get("headline", ""),
                "followers": profile_data.get("followers_count", 0),
                "connections": profile_data.get("connections_count", 0)
            },
            "executive_summary": executive_summary,
            "monthly_activity_notes": monthly_notes,
            "key_recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat(),
            "report_version": "1.0"
        }
    
    def _create_fallback_summary(self, profile_name: str, total_posts: int, avg_engagement: float) -> str:
        """Create fallback executive summary."""
        return f"""Executive Summary for {profile_name}'s LinkedIn Activity

During the analysis period, {profile_name} published {total_posts} posts with an average engagement rate of {avg_engagement:.1%}. The activity shows consistent professional engagement on the LinkedIn platform.

Key highlights include steady content creation and audience interaction. The performance metrics indicate a solid foundation for professional networking and thought leadership.

Strategic focus areas include content optimization and engagement enhancement to further grow influence and reach on the platform."""
    
    def _create_fallback_recommendations(self) -> List[str]:
        """Create fallback recommendations."""
        return [
            "Focus on creating high-quality, value-driven content",
            "Post consistently 3-5 times per week",
            "Engage actively with comments on your posts",
            "Experiment with different content formats",
            "Track engagement metrics to measure success",
            "Network with professionals in your industry",
            "Share insights and thought leadership content"
        ]
    
    def _log_action(self, action: str):
        """Log agent actions."""
        timestamp = datetime.utcnow().isoformat()
        self.audit_log.append({"timestamp": timestamp, "action": action, "agent": "summary"})
        print(f" SummaryAgent: {action}")

# Initialize summary agent
summary_agent = SummaryAgent()

print(" SummaryAgent ready")
print("   → Executive summary generation")
print("   → Actionable recommendations")
print("   → Final report compilation")
