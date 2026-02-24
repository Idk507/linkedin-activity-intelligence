# Enums
class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    ARTICLE = "article"
    CAROUSEL = "carousel"
    POLL = "poll"
    DOCUMENT = "document"

class EngagementType(str, Enum):
    LIKE = "like"
    COMMENT = "comment"
    REPOST = "repost"
    IMPRESSION = "impression"


# Profile Models (simplified for multi-agent use)
class LinkedInProfile(BaseModel):
    user_id: str
    full_name: str
    headline: str
    followers_count: int = 0
    connections_count: int = 0
    industry: Optional[str] = None
    location: Optional[str] = None
    about: Optional[str] = None

class LinkedInPost(BaseModel):
    post_id: str
    user_id: str
    content: str
    content_type: ContentType
    published_at: datetime
    likes_count: int = 0
    comments_count: int = 0
    reposts_count: int = 0
    impressions: int = 0

class MonthlyActivity(BaseModel):
    user_id: str
    month: str
    posts_count: int = 0
    total_impressions: int = 0
    total_likes: int = 0
    engagement_rate: float = 0.0
    content_types: Dict[str, int] = Field(default_factory=dict)
