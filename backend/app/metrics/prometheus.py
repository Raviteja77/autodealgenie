"""
Prometheus Metrics Module
Defines custom application metrics for AutoDealGenie
"""

import logging

from prometheus_client import Counter, Gauge, Histogram, Info

# Application Info
app_info = Info("autodealgenie_app", "AutoDealGenie application information")

# Business Metrics
deals_created = Counter(
    "autodealgenie_deals_created_total",
    "Total number of deals created",
    ["status"],
)

user_signups = Counter(
    "autodealgenie_user_signups_total",
    "Total number of user signups",
)

auth_success = Counter(
    "autodealgenie_auth_success_total",
    "Total number of successful authentication attempts",
)

auth_failures = Counter(
    "autodealgenie_auth_failures_total",
    "Total number of failed authentication attempts",
)

# Vehicle Search Metrics
vehicle_searches = Counter(
    "autodealgenie_vehicle_searches_total",
    "Total number of vehicle searches performed",
    ["search_type"],
)

vehicle_search_duration = Histogram(
    "autodealgenie_vehicle_search_duration_seconds",
    "Time spent processing vehicle searches",
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
)

# Negotiation Metrics
negotiation_sessions = Counter(
    "autodealgenie_negotiation_sessions_total",
    "Total number of negotiation sessions started",
)

negotiation_messages = Counter(
    "autodealgenie_negotiation_messages_total",
    "Total number of negotiation messages exchanged",
    ["role"],  # user or assistant
)

negotiation_duration = Histogram(
    "autodealgenie_negotiation_duration_seconds",
    "Duration of negotiation sessions",
    buckets=[10.0, 30.0, 60.0, 120.0, 300.0, 600.0],
)

# Loan Application Metrics
loan_applications = Counter(
    "autodealgenie_loan_applications_total",
    "Total number of loan applications submitted",
    ["status"],
)

loan_processing_duration = Histogram(
    "autodealgenie_loan_processing_duration_seconds",
    "Time spent processing loan applications",
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# Database Query Metrics
db_query_duration = Histogram(
    "autodealgenie_db_query_duration_seconds",
    "Duration of database queries",
    ["operation", "table"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
)

db_queries_total = Counter(
    "autodealgenie_db_queries_total",
    "Total number of database queries",
    ["operation", "table"],
)

db_query_errors = Counter(
    "autodealgenie_db_query_errors_total",
    "Total number of database query errors",
    ["operation", "table"],
)

# Cache Metrics
cache_hits = Counter(
    "autodealgenie_cache_hits_total",
    "Total number of cache hits",
    ["cache_name"],
)

cache_misses = Counter(
    "autodealgenie_cache_misses_total",
    "Total number of cache misses",
    ["cache_name"],
)

cache_operation_duration = Histogram(
    "autodealgenie_cache_operation_duration_seconds",
    "Duration of cache operations",
    ["operation", "cache_name"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1],
)

# External API Metrics
external_api_requests = Counter(
    "autodealgenie_external_api_requests_total",
    "Total number of external API requests",
    ["api_name", "status"],
)

external_api_duration = Histogram(
    "autodealgenie_external_api_duration_seconds",
    "Duration of external API calls",
    ["api_name"],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
)

external_api_errors = Counter(
    "autodealgenie_external_api_errors_total",
    "Total number of external API errors",
    ["api_name", "error_type"],
)

# LLM/AI Metrics
llm_requests = Counter(
    "autodealgenie_llm_requests_total",
    "Total number of LLM requests",
    ["model", "prompt_type"],
)

llm_tokens_used = Counter(
    "autodealgenie_llm_tokens_used_total",
    "Total number of LLM tokens used",
    ["model", "token_type"],  # prompt or completion
)

llm_request_duration = Histogram(
    "autodealgenie_llm_request_duration_seconds",
    "Duration of LLM requests",
    ["model"],
    buckets=[0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
)

llm_errors = Counter(
    "autodealgenie_llm_errors_total",
    "Total number of LLM errors",
    ["model", "error_type"],
)

# Active Resources Gauges
active_users = Gauge(
    "autodealgenie_active_users",
    "Number of currently active users",
)

active_negotiation_sessions_gauge = Gauge(
    "autodealgenie_active_negotiation_sessions",
    "Number of currently active negotiation sessions",
)

active_searches_gauge = Gauge(
    "autodealgenie_active_searches",
    "Number of currently active vehicle searches",
)


def initialize_metrics():
    """
    Initialize metrics with default values
    Should be called at application startup
    """
    try:
        app_info.info(
            {
                "version": "1.0.0",
                "environment": "development",
            }
        )
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to initialize metrics: {e}")
        # Don't raise - allow application to continue without metrics
