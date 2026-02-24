import os
import json 
import asyncio 
from datetime import datetime , timedelta
from typing import Annotated, Any, Optional, List , Dict , TypedDict, Literal, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
import hashlib
from collections import defaultdict
from enum import Enum
import logging
import structlog 

#reuse data models 
from pydantic import BaseModel, Field
from enum import Enum

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.prebuilt.tool_node import ToolNode
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import AzureChatOpenAI

#load environment variables 
from dotenv import load_dotenv
load_dotenv(Path("../.env"))


# Configure logging 
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger(__name__)



#Azure openai config 
AZURE_OPENAI_ENDPOINT = os.getenv("AI_FOUNDRY_PROJECT_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AI_FOUNDRY_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AI_FOUNDRY_DEPLOYMENT_NAME", "gpt-4.1")
AZURE_OPENAI_API_VERSION = os.getenv("AI_FOUNDRY_API_VERSION", "2024-12-01-preview")


#linkedin data sources 
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
LINKEDIN_LI_AT = os.getenv("LINKEDIN_LI_AT")
PROXYCURL_API_KEY = os.getenv("PROXYCURL_API_KEY")

#Analysis Time window 
ANALYSIS_START_DATE = datetime(2025, 1, 1)
ANALYSIS_END_DATE = datetime(2026, 1, 1)
