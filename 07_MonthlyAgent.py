class MonthlyAnalysisAgent:
    """Agent responsible for creating detailed month-wise activity analysis using AI."""
    
    def __init__(self):
        self.audit_log = []
        logger.info("MonthlyAnalysisAgent initialized")
    
    def process(self, state: LAIEState) -> AgentResponse:
        """Generate detailed month-wise activity notes using AI."""
        logger.info("MonthlyAnalysisAgent processing")
        
        try:
            monthly_analytics = state.get("monthly_analytics", [])
            profile_data = state.get("raw_profile", {})
            
            if not monthly_analytics:
                raise ValueError("No monthly analytics data available")
            
            # Generate AI-powered monthly notes
            monthly_notes = []
            for month_data in monthly_analytics:
                note = self._generate_monthly_note(month_data, profile_data)
                monthly_notes.append(note)
            
            response = AgentResponse(
                success=True,
                data=monthly_notes,
                message=f"Generated {len(monthly_notes)} monthly activity notes",
                next_agent="summary",
                errors=[]
            )
            
            self._log_action(f"Generated {len(monthly_notes)} monthly analysis notes")
            
        except Exception as e:
            logger.error("MonthlyAnalysisAgent failed", error=str(e))
            response = AgentResponse(
                success=False,
                data=None,
                message=f"Monthly analysis failed: {str(e)}",
                next_agent=None,
                errors=[str(e)]
            )
        
        return response
    
    def _generate_monthly_note(self, month_data: Dict[str, Any], profile_data: Dict[str, Any]) -> MonthlyNote:
        """Generate a comprehensive monthly activity note using AI."""
        month = month_data.get("month", "unknown")
        posts_count = month_data.get("posts_count", 0)
        impressions = month_data.get("total_impressions", 0)
        likes = month_data.get("total_likes", 0)
        engagement_rate = month_data.get("engagement_rate", 0)
        content_types = month_data.get("content_types", {})
        
        profile_name = profile_data.get("full_name", "Professional")
        
        # Create AI prompt for monthly analysis
        prompt = f"""As a LinkedIn analytics expert, create a comprehensive monthly activity note for {profile_name} in {month}.
        
        KEY METRICS:
- Posts: {posts_count}
- Total Impressions: {impressions:,}
- Total Likes: {likes}
- Engagement Rate: {engagement_rate:.1%}
- Content Types: {content_types}

Please provide:

1. ACTIVITY SUMMARY: A 2-3 sentence overview of the month's LinkedIn activity

2. KEY ACHIEVEMENTS: 3-4 bullet points highlighting the most important accomplishments or engagement moments

3. CONTENT PERFORMANCE: Analysis of which content types performed best and why

4. ENGAGEMENT HIGHLIGHTS: Notable engagement patterns or viral moments

5. RECOMMENDATIONS: 2-3 actionable suggestions for the next month

6. AI INSIGHTS: Strategic observations about audience behavior and content strategy

Keep the analysis professional, data-driven, and actionable. Focus on patterns and opportunities."""
        
        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            ai_analysis = response.content
            
            # Parse the AI response into structured format
            structured_note = self._parse_ai_response(ai_analysis, month, month_data)
            
        except Exception as e:
            logger.warning(f"AI analysis failed for {month}: {e}")
            structured_note = self._create_fallback_note(month, month_data, profile_name)
        
        return structured_note
    
    def _parse_ai_response(self, ai_response: str, month: str, month_data: Dict[str, Any]) -> MonthlyNote:
        """Parse AI response into structured monthly note format."""
        # Simple parsing logic - in production, use more sophisticated parsing
        lines = ai_response.split('\n')
        
        # Extract sections (simplified)
        activity_summary = ""
        key_achievements = []
        content_performance = {}
        engagement_highlights = []
        recommendations = []
        ai_insights = ""
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if "ACTIVITY SUMMARY" in line.upper() or "1." in line:
                current_section = "summary"
                continue
            elif "KEY ACHIEVEMENTS" in line.upper() or "2." in line:
                current_section = "achievements"
                continue
            elif "CONTENT PERFORMANCE" in line.upper() or "3." in line:
                current_section = "content"
                continue
            elif "ENGAGEMENT HIGHLIGHTS" in line.upper() or "4." in line:
                current_section = "engagement"
                continue
            elif "RECOMMENDATIONS" in line.upper() or "5." in line:
                current_section = "recommendations"
                continue
            elif "AI INSIGHTS" in line.upper() or "6." in line:
                current_section = "insights"
                continue
            
            # Add content to current section
            if current_section == "summary":
                if not activity_summary:
                    activity_summary = line
                else:
                    activity_summary += " " + line
            elif current_section == "achievements" and line.startswith(("-", "•")):
                key_achievements.append(line.lstrip("-• "))
            elif current_section == "content":
                content_performance["analysis"] = content_performance.get("analysis", "") + line + " "
            elif current_section == "engagement" and line.startswith(("-", "•")):
                engagement_highlights.append(line.lstrip("-• "))
            elif current_section == "recommendations" and line.startswith(("-", "•")):
                recommendations.append(line.lstrip("-• "))
            elif current_section == "insights":
                ai_insights += line + " "
        
        return MonthlyNote(
            month=month,
            activity_summary=activity_summary.strip(),
            key_achievements=key_achievements[:4],  # Limit to 4
            content_performance=content_performance,
            engagement_highlights=engagement_highlights[:3],  # Limit to 3
            recommendations=recommendations[:3],  # Limit to 3
            ai_insights=ai_insights.strip()
        )
    
    def _create_fallback_note(self, month: str, month_data: Dict[str, Any], profile_name: str) -> MonthlyNote:
        """Create a fallback monthly note when AI analysis fails."""
        return MonthlyNote(
            month=month,
            activity_summary=f"{profile_name} published {month_data.get('posts_count', 0)} posts in {month}, generating {month_data.get('total_impressions', 0):,} impressions.",
            key_achievements=[f"Achieved {month_data.get('engagement_rate', 0):.1%} engagement rate"],
            content_performance={"analysis": f"Primary content type: {max(month_data.get('content_types', {}), key=month_data.get('content_types', {}).get, default='text')}"},
            engagement_highlights=[f"{month_data.get('total_likes', 0)} total likes received"],
            recommendations=["Continue current content strategy", "Experiment with different posting times"],
            ai_insights="Analysis generated with limited data. Consider providing more detailed metrics for deeper insights."
        )
    
    def _log_action(self, action: str):
        """Log agent actions."""
        timestamp = datetime.utcnow().isoformat()
        self.audit_log.append({"timestamp": timestamp, "action": action, "agent": "monthly_analysis"})
        print(f"MonthlyAnalysisAgent: {action}")

# Initialize monthly analysis agent
monthly_analysis_agent = MonthlyAnalysisAgent()

print(" MonthlyAnalysisAgent ready")
print("   → AI-powered monthly activity notes")
print("   → Structured analysis format")
print("   → Fallback handling for API failures")
