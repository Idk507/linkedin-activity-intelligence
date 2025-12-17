linkedin-activity-intelligence/
│
├── README.md
├── pyproject.toml
├── .env.example
│
├── app/
│   ├── main.py
│
│   ├── api/
│   │   ├── v1/
│   │   │   ├── routes/
│   │   │   │   ├── auth.py
│   │   │   │   ├── ingest.py
│   │   │   │   ├── analytics.py
│   │   │   │   ├── insights.py
│   │   │   │   └── reports.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── security.py
│   │   └── azure.py                 # Azure credentials & clients
│
│   ├── ingestion/
│   │   ├── linkedin/
│   │   │   ├── api_client.py
│   │   │   ├── export_parser.py
│   │   │   └── dom_extractor.py
│   │   └── normalizer.py
│
│   ├── models/
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── engagement.py
│   │   ├── follower.py
│   │   └── network.py
│
│   ├── repositories/
│   │   ├── post_repo.py
│   │   ├── engagement_repo.py
│   │   ├── follower_repo.py
│   │   └── network_repo.py
│
│   ├── analytics/
│   │   ├── time_series/
│   │   ├── content/
│   │   ├── network/
│   │   ├── nlp/
│   │   └── scoring/
│
│   ├── context_store/
│   │   ├── __init__.py
│   │   ├── snapshot_builder.py      # Builds yearly context
│   │   ├── snapshot_schema.py       # JSON schemas
│   │   └── snapshot_repo.py
│
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py                # MCP Server entry
│   │   ├── registry.py              # Tool registry
│   │   ├── schemas.py               # Tool input/output schemas
│   │   ├── tools/
│   │   │   ├── activity.py          # get_activity_window
│   │   │   ├── posts.py             # get_top_posts
│   │   │   ├── growth.py            # get_follower_growth
│   │   │   ├── network.py           # get_engagement_network
│   │   │   └── topics.py
│   │   └── auth.py
│
│   ├── ai/
│   │   ├── llm/
│   │   │   ├── azure_openai_client.py
│   │   │   ├── mcp_client.py        # MCP-aware client
│   │   │   └── response_parser.py
│   │   ├── prompts/
│   │   │   ├── yearly_review.txt
│   │   │   ├── strategist.txt
│   │   │   └── diagnostics.txt
│   │   ├── insight_engine.py
│   │   └── agent_orchestrator.py
│
│   ├── jobs/
│   │   ├── ingestion_job.py
│   │   ├── analytics_job.py
│   │   ├── context_snapshot_job.py
│   │   ├── insight_job.py
│   │   └── report_job.py
│
│   ├── reports/
│   │   ├── pdf_generator.py
│   │   └── templates/
│
│   ├── utils/
│   │   ├── date_utils.py
│   │   ├── validators.py
│   │   └── retry.py
│
│   └── tests/
│
├── worker/
│   ├── celery_app.py
│   └── tasks.py
│
├── infra/
│   ├── docker/
│   ├── terraform/
│   └── k8s/
│
└── scripts/
    ├── backfill_2025.py
    └── rebuild_context.py
