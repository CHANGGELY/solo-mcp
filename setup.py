#!/usr/bin/env python3
"""Setup script for Solo MCP."""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="solo-mcp",
    version="0.1.1",
    author="Solo MCP Team",
    author_email="contact@solo-mcp.dev",
    description="智能代理协作平台 - 基于 MCP 协议的多角色任务编排系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/solo-mcp",
    packages=find_packages(),
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
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "solo-mcp=solo_mcp:main",
            "solo-mcp-server=solo_mcp.mcp_server:run_server",
        ],
    },
    include_package_data=True,
    package_data={
        "solo_mcp": ["config/*.json", "templates/*.json"],
    },
    zip_safe=False,
    keywords="mcp, ai, agent, orchestration, memory, context",
    project_urls={
        "Bug Reports": "https://github.com/your-username/solo-mcp/issues",
        "Source": "https://github.com/your-username/solo-mcp",
        "Documentation": "https://solo-mcp.readthedocs.io/",
    },
)