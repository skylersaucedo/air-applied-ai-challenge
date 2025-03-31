from setuptools import find_packages, setup

setup(
    name="air-applied-ai-challenge",
    version="0.1.0",
    packages=find_packages(include=["app", "app.*"]),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "pytest==7.4.3",
        "pytest-asyncio==0.21.1",
        "pytest-cov==4.1.0",
        "httpx==0.25.2",
        "sqlalchemy==2.0.23",
        "redis==5.0.1",
        "qdrant-client==1.6.4",
        "fakeredis==2.20.0",
        "pytest-mock==3.12.0",
        "transformers==4.34.0",
        "torch==2.1.1",
        "numpy==1.26.2",
    ],
    python_requires=">=3.8",
) 