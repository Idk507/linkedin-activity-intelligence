class IngestionAgent:
    """Agent responsible for collecting LinkedIn data from various sources."""
    
    def __init__(self):
        self.audit_log = []
        logger.info("IngestionAgent initialized")
    
    def process(self, state: LAIEState) -> AgentResponse:
        """Process data ingestion for the given LinkedIn profile."""
        public_id = state["public_id"]
        data_sources = state["data_sources"]
        
        logger.info(f"IngestionAgent processing for public_id={public_id}")
        
        try:
            # Attempt data collection
            profile, posts = self._collect_data(public_id, data_sources)
            
            # Validate data quality
            quality_score = self._assess_data_quality(profile, posts)
            
            # Convert to dict format for state
            profile_dict = profile.dict() if hasattr(profile, 'dict') else profile
            posts_list = [post.dict() if hasattr(post, 'dict') else post for post in posts]
            
            response = AgentResponse(
                success=True,
                data={
                    "profile": profile_dict,
                    "posts": posts_list,
                    "quality_score": quality_score
                },
                message=f"Successfully collected data for {public_id}",
                next_agent="analytics",
                errors=[]
            )
            
            self._log_action(f"Data ingestion completed for {public_id}")
            
        except Exception as e:
            logger.error("IngestionAgent failed", error=str(e))
            response = AgentResponse(
                success=False,
                data=None,
                message=f"Data ingestion failed: {str(e)}",
                next_agent=None,
                errors=[str(e)]
            )
        
        return response
    
    def _collect_data(self, public_id: str, data_sources: Dict[str, Any]) -> tuple:
        """Collect data from available sources."""
        # Priority: GDPR export > Proxycurl > linkedin-api
        
        if data_sources.get("gdpr_export"):
            return self._parse_gdpr_export(data_sources["gdpr_export"], public_id)
        
        if data_sources.get("proxycurl_api_key"):
            return self._fetch_proxycurl_data(public_id, data_sources["proxycurl_api_key"])
        
        if data_sources.get("linkedin_credentials"):
            return self._fetch_linkedin_api_data(public_id, data_sources["linkedin_credentials"])
        
        raise ValueError("No valid data source provided")
    
    def _parse_gdpr_export(self, zip_path: str, public_id: str) -> tuple:
        """Parse GDPR export (simplified implementation)."""
        # In production, this would parse actual GDPR export
        # For demo, return mock data
        profile = LinkedInProfile(
            user_id=public_id,
            full_name="Demo User",
            headline="Professional Title",
            followers_count=1000,
            connections_count=500
        )
        
        # Generate mock posts for the analysis period
        posts = []
        current_date = ANALYSIS_START_DATE
        post_id = 0
        
        while current_date < ANALYSIS_END_DATE:
            # Add 2-5 posts per month
            posts_this_month = []
            num_posts = 2 + (hash(public_id + current_date.strftime("%Y-%m")) % 4)
            
            for i in range(num_posts):
                post_date = current_date + timedelta(days=i * 7)  # Spread posts
                if post_date >= ANALYSIS_END_DATE:
                    break
                
                posts.append(LinkedInPost(
                    post_id=f"post_{post_id}",
                    user_id=public_id,
                    content=f"Sample LinkedIn post content for {post_date.strftime('%B %Y')}",
                    content_type=ContentType.TEXT,
                    published_at=post_date,
                    likes_count=10 + (hash(str(post_id)) % 90),
                    comments_count=1 + (hash(str(post_id + 1)) % 9),
                    reposts_count=0 + (hash(str(post_id + 2)) % 5),
                    impressions=100 + (hash(str(post_id + 3)) % 900)
                ))
                post_id += 1
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return profile, posts
    
    def _fetch_proxycurl_data(self, public_id: str, api_key: str) -> tuple:
        """Fetch data from Proxycurl API."""
        import requests
        
        try:
            # Proxycurl API endpoint for profile data
            url = "https://nubela.co/proxycurl/api/v2/linkedin"
            headers = {
                'Authorization': f'Bearer {api_key}'
            }
            params = {
                'url': f'https://www.linkedin.com/in/{public_id}',
                'fallback_to_cache': 'on-error'
            }
            
            logger.info(f"Fetching profile data from Proxycurl for public_id={public_id}")
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract profile information
            profile = LinkedInProfile(
                user_id=public_id,
                full_name=data.get('full_name', f'User {public_id}'),
                headline=data.get('headline', data.get('occupation', 'Professional')),
                followers_count=data.get('follower_count', 0),
                connections_count=data.get('connections', 0),
                industry=data.get('industry'),
                location=data.get('city', {}).get('full') if data.get('city') else None,
                about=data.get('summary')
            )
            
            # Proxycurl doesn't provide posts data, return empty list
            posts = []
            self._log_action(f"Successfully fetched Proxycurl data for {public_id}")
            
            return profile, posts
            
        except requests.exceptions.RequestException as e:
            logger.error("Proxycurl API error", error=str(e))
            raise ValueError(f"Failed to fetch Proxycurl data: {str(e)}")
        except Exception as e:
            logger.error("Proxycurl data processing error", error=str(e))
            raise ValueError(f"Failed to process Proxycurl data: {str(e)}")
    
    def _fetch_linkedin_api_data(self, public_id: str, credentials: Dict) -> tuple:
        """Fetch data using linkedin-api."""
        try:
            from linkedin_api import Linkedin
            
            # Initialize LinkedIn client
            email = credentials.get("email") or os.getenv("LINKEDIN_EMAIL")
            password = credentials.get("password") or os.getenv("LINKEDIN_PASSWORD")
            li_at = credentials.get("li_at") or os.getenv("LINKEDIN_LI_AT")
            
            if li_at:
                # Use li_at cookie for authentication
                api = Linkedin("", "", cookies={"li_at": li_at})
            elif email and password:
                # Use email/password authentication
                api = Linkedin(email, password)
            else:
                raise ValueError("No valid LinkedIn credentials provided")
            
            logger.info(f"Fetching profile data from LinkedIn API for public_id={public_id}")
            
            # Get profile data
            profile_data = api.get_profile(public_id)
            
            # Extract profile information
            profile = LinkedInProfile(
                user_id=public_id,
                full_name=profile_data.get("firstName", "") + " " + profile_data.get("lastName", "") if profile_data.get("firstName") else f"User {public_id}",
                headline=profile_data.get("headline", "Professional"),
                followers_count=profile_data.get("followerCount", 0),
                connections_count=profile_data.get("connectionsCount", 0),
                industry=profile_data.get("industryName"),
                location=profile_data.get("locationName"),
                about=profile_data.get("summary")
            )
            
            # Get posts/activity data
            logger.info(f"Fetching posts data from LinkedIn API for public_id={public_id}")
            urn_id = profile_data.get("public_id") or public_id
            
            # Get recent posts (last 365 days)
            posts_data = api.get_profile_posts(urn_id, post_count=50)  # Get up to 50 recent posts
            posts = []
            
            for post_item in posts_data.get("elements", []):
                post = post_item.get("update", {}).get("share", {})
                if not post:
                    continue
                
                # Extract post information
                post_id = str(post.get("urn", "").split(":")[-1])
                content = post.get("text", {}).get("text", "")
                published_at_str = post.get("created", {}).get("time")
                
                # Convert timestamp to datetime
                if published_at_str:
                    try:
                        published_at = datetime.fromtimestamp(int(published_at_str) / 1000)
                    except:
                        published_at = ANALYSIS_START_DATE
                else:
                    published_at = ANALYSIS_START_DATE
                
                # Skip posts outside analysis window
                if published_at < ANALYSIS_START_DATE or published_at >= ANALYSIS_END_DATE:
                    continue
                
                # Get engagement metrics
                social_counts = post.get("socialDetail", {}).get("totalSocialActivityCounts", {})
                likes_count = social_counts.get("numLikes", 0)
                comments_count = social_counts.get("numComments", 0)
                reposts_count = social_counts.get("numShares", 0)
                impressions = social_counts.get("numImpressions", 0)
                
                # Determine content type
                content_type = ContentType.TEXT
                if post.get("content", {}).get("images"):
                    content_type = ContentType.IMAGE
                elif post.get("content", {}).get("videos"):
                    content_type = ContentType.VIDEO
                
                posts.append(LinkedInPost(
                    post_id=post_id,
                    user_id=public_id,
                    content=content,
                    content_type=content_type,
                    published_at=published_at,
                    likes_count=likes_count,
                    comments_count=comments_count,
                    reposts_count=reposts_count,
                    impressions=impressions
                ))
            
            self._log_action(f"Successfully fetched LinkedIn API data for {public_id}: {len(posts)} posts")
            
            return profile, posts
            
        except ImportError as e:
            logger.error("linkedin-api package not installed", error=str(e))
            raise ValueError("linkedin-api package required for LinkedIn API data fetching")
        except Exception as e:
            logger.error("LinkedIn API error", error=str(e))
            raise ValueError(f"Failed to fetch LinkedIn API data: {str(e)}")
