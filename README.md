# GenAI Playground

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/kubernetes-ready-blue.svg)](https://kubernetes.io/)
[![Claude API](https://img.shields.io/badge/Claude-API-orange.svg)](https://www.anthropic.com/)

## Overview

**GenAI Playground** is a comprehensive prototyping environment for Generative AI technologies. This repository serves as a practical toolkit for exploring Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), vector databases, and agent-based systems.

## 🚀 Planned Features

- **Claude API Integration**: Complete implementation of Anthropic's Claude API including chat, streaming, and function calling
- **RAG Pipelines**: End-to-end retrieval-augmented generation with document ingestion and semantic search
- **Vector Databases**: Integration with ChromaDB, Pinecone, and custom embedding strategies
- **Agent Systems**: Tool-calling agents and multi-agent orchestration
- **Production Ready**: Dockerized deployment, environment configuration, and CI/CD patterns
- **Kubernetes Support**: Helm charts and K8s manifests for orchestration
- **Performance Monitoring**: Built-in metrics and logging for AI operations

## 🛠️ Technology Stack

| Category | Technologies |
|----------|--------------|
| **Languages** | Python 3.12+, TypeScript (experimental) |
| **LLM APIs** | Claude (Anthropic), OpenAI (optional) |
| **Vector DBs** | ChromaDB, Pinecone, FAISS |
| **Frameworks** | LangChain, LangGraph, FastAPI |
| **Containerization** | Docker, Docker Compose |
| **Orchestration** | Kubernetes, Helm, Minikube |
| **AI Assistants** | GitHub Copilot optimized development |
| **ML Tools** | Sentence-Transformers, HuggingFace |
| **Development** | VSCode with Dev Containers |

## 📋 Prerequisites

- **Python 3.12+** (see installation below)
- **Docker** (20.10+)
- **Kubernetes** (optional - for K8s deployment)
- **VSCode** (recommended)
- **Git** (2.30+)

## 🐍 Python 3.12 Installation

### On macOS (Apple Silicon/Intel)

```bash
# Using Homebrew
brew install python@3.12

# Verify installation
python3.12 --version
```
