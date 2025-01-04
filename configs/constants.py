import os


APP_TITLE = "RAG based sitemap search"
APP_DESCRIPTION = """
A service that crawls a website sitemap, extracts structured content, and provides an API to search and summarize data using LLM.
"""
APP_VERSION = "0.0.1"
APP_DEBUG = True

CONTACT = dict(
    name = "Developer",
    url = None,
    email = "hariharanmh2@gmail.com"
)

OPENAPI_URL = "/api/v1/openapi.json"
DOCS_URL = "/api/v1/docs"
REDOC_URL = "/api/v1/redoc"