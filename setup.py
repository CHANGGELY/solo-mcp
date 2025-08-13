#!/usr/bin/env python3
from setuptools import setup, find_packages

# Read the contents of README file for long description
try:
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "智能代理协作平台 - 基于 MCP 协议的多角色任务编排系统"

# Read requirements from requirements.txt
try:
    with open("requirements.txt", "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    requirements = [
        "fastmcp>=0.3.0",
        "mcp>=1.1.0",
        "pydantic>=2.0.0",
        "toml>=0.10.0",
        "python-dateutil>=2.8.0",
    ]

setup(
    name="solo-mcp",
    version="0.1.1",
    description="智能代理协作平台 - 基于 MCP 协议的多角色任务编排系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Solo MCP Team",
    author_email="contact@solo-mcp.dev",
    url="https://github.com/CHANGGELY/solo-mcp",
    license="Apache-2.0",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="mcp ai agent orchestration memory context",
    entry_points={
        "console_scripts": [
            "solo-mcp=solo_mcp:main",
            "solo-mcp-server=solo_mcp.mcp_server:run_server",
        ],
    },
    package_data={
        "solo_mcp": ["config/*.json", "templates/*.json"],
    },
    zip_safe=False,
)