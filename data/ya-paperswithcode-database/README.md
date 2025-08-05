create a searching demo here


# Local Paper Search Agent

A semantic search-based intelligent academic paper retrieval system inspired by the PASA (Paper Search Agent) architecture, using a local paper database instead of online searches.

## Project Overview

This project implements an intelligent paper search agent capable of:
- Automatically generating multiple search strategies based on user queries.
- Retrieving papers using semantic similarity.
- Discovering additional relevant papers through multi-layer expansion.
- Scoring and ranking retrieval results based on relevance.

## Key Features

- **Semantic Search**: Utilizes the Sentence-BERT model for semantic embeddings, supporting natural language queries.
- **Multi-layer Expansion**: Deep exploration through recommendations of similar papers.
- **Parallel Processing**: Multi-threaded concurrent searches to improve efficiency.
- **Flexible Configuration**: Supports custom search parameters and expansion strategies.
- **Local Operation**: Fully operates on local data without the need for external APIs.

## System Architecture

- User Query  
  - Query Generation  
    - Generates multiple exclusive search queries  
  - Initial Search  
    - Retrieves semantically relevant papers  
    - Filters based on relevance scores  
  - Multi-layer Expansion  
    - Layer 1: Similarity-based expansion  
    - Layer 2: Deep expansion