class AnalyticsAgent:
    """Agent responsible for performing deterministic analytics on LinkedIn data."""
    
    def __init__(self):
        self.audit_log = []
        logger.info("AnalyticsAgent initialized")
    
    def process(self, state: LAIEState) -> AgentResponse:
        """Process analytics on the collected LinkedIn data."""
        logger.info("AnalyticsAgent processing")
        
        try:
            # Extract data from state
            profile_data = state.get("raw_profile")
            posts_data = state.get("raw_posts", [])
            
            if not profile_data or not posts_data:
                raise ValueError("Insufficient data for analytics")
            
            # Convert to model objects
            profile = LinkedInProfile(**profile_data)
            posts = [LinkedInPost(**post_data) for post_data in posts_data]
            
            # Perform analytics
            monthly_analytics = self._compute_monthly_analytics(profile, posts)
            content_performance = self._compute_content_performance(posts)
            temporal_patterns = self._compute_temporal_patterns(posts)
            
            response = AgentResponse(
                success=True,
                data={
                    "monthly_analytics": [ma.dict() if hasattr(ma, 'dict') else ma for ma in monthly_analytics],
                    "content_performance": content_performance,
                    "temporal_patterns": temporal_patterns
                },
                message="Analytics computation completed successfully",
                next_agent="monthly_analysis",
                errors=[]
            )
            
            self._log_action("Analytics computation completed")
            
        except Exception as e:
            logger.error("AnalyticsAgent failed", error=str(e))
            response = AgentResponse(
                success=False,
                data=None,
                message=f"Analytics computation failed: {str(e)}",
                next_agent=None,
                errors=[str(e)]
            )
        
        return response
    
    def _compute_monthly_analytics(self, profile: LinkedInProfile, posts: List[LinkedInPost]) -> List[MonthlyActivity]:
        """Compute monthly activity analytics."""
        monthly_data = defaultdict(lambda: {
            "posts_count": 0,
            "total_impressions": 0,
            "total_likes": 0,
            "total_comments": 0,
            "total_reposts": 0,
            "content_types": defaultdict(int)
        })
        
        for post in posts:
            month_key = post.published_at.strftime("%Y-%m")
            month_data = monthly_data[month_key]
            
            month_data["posts_count"] += 1
            month_data["total_impressions"] += post.impressions
            month_data["total_likes"] += post.likes_count
            month_data["total_comments"] += post.comments_count
            month_data["total_reposts"] += post.reposts_count
            month_data["content_types"][post.content_type.value] += 1
        
        # Convert to MonthlyActivity objects
        monthly_activities = []
        for month_key, data in sorted(monthly_data.items()):
            total_engagements = data["total_likes"] + data["total_comments"] + data["total_reposts"]
            engagement_rate = total_engagements / data["total_impressions"] if data["total_impressions"] > 0 else 0
            
            monthly_activities.append(MonthlyActivity(
                user_id=profile.user_id,
                month=month_key,
                posts_count=data["posts_count"],
                total_impressions=data["total_impressions"],
                total_likes=data["total_likes"],
                engagement_rate=engagement_rate,
                content_types=dict(data["content_types"])
            ))
        
        return monthly_activities
    
    def _compute_content_performance(self, posts: List[LinkedInPost]) -> Dict[str, Any]:
        """Compute content type performance analytics."""
        if not posts:
            return {}
        
        content_stats = defaultdict(lambda: {
            "count": 0,
            "total_impressions": 0,
            "total_engagements": 0,
            "avg_impressions": 0,
            "avg_engagements": 0,
            "engagement_rate": 0
        })
        
        for post in posts:
            ct = post.content_type.value
            stats = content_stats[ct]
            
            stats["count"] += 1
            stats["total_impressions"] += post.impressions
            stats["total_engagements"] += post.likes_count + post.comments_count + post.reposts_count
        
        # Calculate averages
        for ct, stats in content_stats.items():
            if stats["count"] > 0:
                stats["avg_impressions"] = stats["total_impressions"] / stats["count"]
                stats["avg_engagements"] = stats["total_engagements"] / stats["count"]
                stats["engagement_rate"] = stats["total_engagements"] / stats["total_impressions"] if stats["total_impressions"] > 0 else 0
        
        # Find best performing type
        best_type = max(content_stats.items(), key=lambda x: x[1]["avg_impressions"]) if content_stats else None
        
        return {
            "content_stats": dict(content_stats),
            "best_performing_type": best_type[0] if best_type else None,
            "total_posts_analyzed": len(posts)
        }
    
    def _compute_temporal_patterns(self, posts: List[LinkedInPost]) -> Dict[str, Any]:
        """Compute temporal posting patterns."""
        if not posts:
            return {}
        
        # Analyze posting patterns
        posts_by_weekday = defaultdict(int)
        posts_by_hour = defaultdict(int)
        posts_by_month = defaultdict(int)
        
        for post in posts:
            posts_by_weekday[post.published_at.weekday()] += 1
            posts_by_hour[post.published_at.hour] += 1
            posts_by_month[post.published_at.strftime("%Y-%m")] += 1
        
        # Calculate posting consistency
        total_days = (ANALYSIS_END_DATE - ANALYSIS_START_DATE).days
        active_days = len(set(post.published_at.date() for post in posts))
        posting_consistency = active_days / total_days if total_days > 0 else 0
        
        # Find optimal posting times
        best_weekday = max(posts_by_weekday.items(), key=lambda x: x[1])[0] if posts_by_weekday else None
        best_hour = max(posts_by_hour.items(), key=lambda x: x[1])[0] if posts_by_hour else None
        
        weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        return {
            "posting_consistency": posting_consistency,
            "active_days": active_days,
            "total_days": total_days,
            "best_posting_weekday": weekday_names[best_weekday] if best_weekday is not None else None,
            "best_posting_hour": best_hour,
            "posts_by_month": dict(posts_by_month),
            "avg_posts_per_day": len(posts) / total_days if total_days > 0 else 0
        }
    
    def _log_action(self, action: str):
        """Log agent actions."""
        timestamp = datetime.utcnow().isoformat()
        self.audit_log.append({"timestamp": timestamp, "action": action, "agent": "analytics"})
        print(f"AnalyticsAgent: {action}")

# Initialize analytics agent
analytics_agent = AnalyticsAgent()

print(" AnalyticsAgent ready")
print("   → Monthly activity aggregation")
print("   → Content performance analysis")
print("   → Temporal pattern recognition")
