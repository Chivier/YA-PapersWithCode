# semantic_search.py
import json
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import torch
from typing import List, Dict, Optional, Union
import faiss
from datetime import datetime
from pathlib import Path
import os

class SemanticSearchEngine:
    def __init__(self, data_source: Union[str, list, None] = None, model_name: str = 'all-MiniLM-L6-v2', 
                 is_dataset: bool = False, use_prebuilt: bool = True):
        """Initialize semantic search engine with paper or dataset database
        
        Args:
            data_source: File path, list of data, or None (to load prebuilt embeddings)
            model_name: Name of the sentence transformer model
            is_dataset: Whether this is for datasets (True) or papers (False)
            use_prebuilt: Whether to try loading prebuilt embeddings first
        """
        self.is_dataset = is_dataset
        self.model = None  # Lazy load model only when needed
        self.model_name = model_name
        
        # Try to load prebuilt embeddings first
        if use_prebuilt:
            embeddings_file = 'embeddings/datasets_embeddings.pkl' if is_dataset else 'embeddings/papers_embeddings.pkl'
            faiss_file = embeddings_file.replace('.pkl', '.faiss')
            
            if os.path.exists(embeddings_file) and os.path.exists(faiss_file):
                print(f"Loading prebuilt embeddings from {embeddings_file}...")
                with open(embeddings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.embeddings = data['embeddings']
                    self.data = data['datasets'] if is_dataset else data['papers']
                    
                # Load FAISS index
                self.index = faiss.read_index(faiss_file)
                
                # Set compatibility attributes
                if not is_dataset:
                    self.papers = self.data
                    self.paper_embeddings = self.embeddings
                else:
                    self.datasets = self.data
                    self.dataset_embeddings = self.embeddings
                
                print(f"✓ Loaded prebuilt embeddings for {len(self.data)} items")
                return
        
        # Fall back to building embeddings from scratch
        if data_source is None:
            raise ValueError("data_source is required when prebuilt embeddings are not available")
            
        # Force CPU usage for sentence transformer
        device = torch.device('cpu')
        self.model = SentenceTransformer(model_name, device=device)
        
        if isinstance(data_source, str):
            self.data = self._load_from_file(data_source)
        elif isinstance(data_source, list):
            self.data = data_source
        else:
            raise ValueError("data_source must be either a file path string or a list")
            
        # For backward compatibility
        if not is_dataset:
            self.papers = self.data
            self.paper_embeddings = None
        else:
            self.datasets = self.data
            self.dataset_embeddings = None
            
        self.embeddings = None
        self.index = None
        self._build_index()
    
    def _load_from_file(self, file_path: str) -> List[Dict]:
        """Load data from JSON file"""
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def _load_papers(self, papers_path: str) -> List[Dict]:
        """Load papers from JSON file (backward compatibility)"""
        return self._load_from_file(papers_path)
    
    def _build_index(self):
        """Build FAISS index for semantic search"""
        if self.model is None:
            # Force CPU usage for sentence transformer
            device = torch.device('cpu')
            self.model = SentenceTransformer(self.model_name, device=device)
            
        # Create text representations
        texts = []
        
        if self.is_dataset:
            for item in self.data:
                text = f"{item.get('name', '')} {item.get('full_name', '')} {item.get('description', '')}"
                if item.get('modalities'):
                    text += " " + " ".join(item.get('modalities', []))
                if item.get('languages'):
                    text += " " + " ".join(item.get('languages', []))
                texts.append(text)
            print("Building embeddings for datasets...")
        else:
            for paper in self.papers:
                text = f"{paper['title']} {paper.get('abstract', '')}"
                if paper.get('tasks'):
                    text += " " + " ".join(paper['tasks'])
                texts.append(text)
            print("Building embeddings for papers...")
        
        # Generate embeddings
        self.embeddings = self.model.encode(texts, show_progress_bar=False)
        
        # Store specific embeddings for backward compatibility
        if not self.is_dataset:
            self.paper_embeddings = self.embeddings
        else:
            self.dataset_embeddings = self.embeddings
        
        # Build FAISS index
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings.astype('float32'))
        
        data_type = "datasets" if self.is_dataset else "papers"
        print(f"Index built with {len(self.data)} {data_type}")
    
    def search_by_query(self, query: str, num_results: int = 10, end_date: Optional[str] = None) -> List[str]:
        """Search papers by query and return arxiv IDs"""
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(query_embedding.astype('float32'), num_results * 2)
        
        arxiv_ids = []
        for idx in indices[0]:
            if idx < len(self.papers):
                paper = self.papers[idx]
                
                # Filter by date if specified
                if end_date and paper.get('date'):
                    try:
                        paper_date = datetime.strptime(paper['date'], '%Y-%m-%d')
                        end_datetime = datetime.strptime(end_date, '%Y%m%d')
                        if paper_date > end_datetime:
                            continue
                    except:
                        pass
                
                if paper.get('arxiv_id'):
                    arxiv_ids.append(paper['arxiv_id'])
                    
                if len(arxiv_ids) >= num_results:
                    break
        
        return arxiv_ids
    
    def search_by_arxiv_id(self, arxiv_id: str) -> Optional[Dict]:
        """Get paper details by arxiv ID"""
        for paper in self.papers:
            if paper.get('arxiv_id') == arxiv_id:
                return {
                    'title': paper.get('title', ''),
                    'abstract': paper.get('abstract', ''),
                    'arxiv_id': arxiv_id,
                    'authors': paper.get('authors', []),
                    'tasks': paper.get('tasks', []),
                    'date': paper.get('date', ''),
                    'url_pdf': paper.get('url_pdf', ''),
                    'url_abs': paper.get('url_abs', '')
                }
        return None
    
    def search_by_title(self, title: str) -> Optional[Dict]:
        """Search paper by title using semantic similarity"""
        title_embedding = self.model.encode([title])
        distances, indices = self.index.search(title_embedding.astype('float32'), 5)
        
        # Find best matching paper by title
        best_match = None
        best_score = float('inf')
        
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.papers):
                paper = self.papers[idx]
                if paper.get('title'):
                    # Simple title similarity check
                    if title.lower() in paper['title'].lower() or paper['title'].lower() in title.lower():
                        if distance < best_score:
                            best_score = distance
                            best_match = paper
        
        if best_match:
            return {
                'title': best_match.get('title', ''),
                'abstract': best_match.get('abstract', ''),
                'arxiv_id': best_match.get('arxiv_id', ''),
                'authors': best_match.get('authors', []),
                'tasks': best_match.get('tasks', []),
                'date': best_match.get('date', ''),
                'url_pdf': best_match.get('url_pdf', ''),
                'url_abs': best_match.get('url_abs', '')
            }
        return None
    
    def search_similar_papers(self, arxiv_id: str, num_results: int = 10) -> List[Dict]:
        """Find similar papers based on a given paper"""
        # Find the paper index
        paper_idx = None
        for idx, paper in enumerate(self.papers):
            if paper.get('arxiv_id') == arxiv_id:
                paper_idx = idx
                break
        
        if paper_idx is None:
            return []
        
        # Search for similar papers
        paper_embedding = self.paper_embeddings[paper_idx:paper_idx+1]
        distances, indices = self.index.search(paper_embedding.astype('float32'), num_results + 1)
        
        similar_papers = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx != paper_idx and idx < len(self.papers):
                paper = self.papers[idx]
                similar_papers.append({
                    'title': paper.get('title', ''),
                    'abstract': paper.get('abstract', ''),
                    'arxiv_id': paper.get('arxiv_id', ''),
                    'authors': paper.get('authors', []),
                    'tasks': paper.get('tasks', []),
                    'date': paper.get('date', ''),
                    'url_pdf': paper.get('url_pdf', ''),
                    'url_abs': paper.get('url_abs', ''),
                    'similarity_score': float(1 / (1 + distance))  # Convert distance to similarity
                })
        
        return similar_papers
    
    def search_by_query_datasets(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search datasets by query"""
        if not self.is_dataset:
            raise ValueError("This engine is not configured for dataset search")
        
        # Lazy load model if needed (on CPU)
        if self.model is None:
            device = torch.device('cpu')
            self.model = SentenceTransformer(self.model_name, device=device)
            
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(query_embedding.astype('float32'), num_results)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.datasets):
                dataset = self.datasets[idx].copy()
                dataset['similarity_score'] = float(1 / (1 + distance))
                
                # Add ID field if missing
                if 'id' not in dataset or not dataset['id']:
                    if 'url' in dataset and dataset['url']:
                        # Extract ID from URL
                        url_parts = dataset['url'].rstrip('/').split('/')
                        if len(url_parts) > 0:
                            dataset['id'] = url_parts[-1]
                        else:
                            dataset['id'] = dataset.get('name', '').lower().replace(' ', '-')
                    else:
                        dataset['id'] = dataset.get('name', '').lower().replace(' ', '-')
                
                results.append(dataset)
        
        return results
    
    def extend_datasets_by_similarity(self, query_datasets: List[Dict], candidate_datasets: List[Dict], num_results: int = 10) -> List[Dict]:
        """Extend dataset results based on similarity"""
        if not self.is_dataset:
            raise ValueError("This engine is not configured for dataset search")
        
        # Create embeddings for query datasets
        query_texts = []
        for dataset in query_datasets:
            text = f"{dataset.get('name', '')} {dataset.get('description', '')}"
            query_texts.append(text)
        
        if not query_texts:
            return []
            
        # Lazy load model if needed (on CPU)
        if self.model is None:
            device = torch.device('cpu')
            self.model = SentenceTransformer(self.model_name, device=device)
            
        query_embeddings = self.model.encode(query_texts)
        
        # Find similar datasets from candidates
        extended_results = []
        seen_ids = set()
        
        for query_emb in query_embeddings:
            distances, indices = self.index.search(query_emb.reshape(1, -1).astype('float32'), num_results)
            
            for idx, distance in zip(indices[0], distances[0]):
                if idx < len(self.datasets):
                    dataset = self.datasets[idx]
                    
                    # Generate ID if missing
                    if 'id' not in dataset or not dataset['id']:
                        if 'url' in dataset and dataset['url']:
                            url_parts = dataset['url'].rstrip('/').split('/')
                            if len(url_parts) > 0:
                                dataset['id'] = url_parts[-1]
                            else:
                                dataset['id'] = dataset.get('name', '').lower().replace(' ', '-')
                        else:
                            dataset['id'] = dataset.get('name', '').lower().replace(' ', '-')
                    
                    dataset_id = dataset.get('id', dataset.get('name', ''))
                    
                    if dataset_id not in seen_ids:
                        seen_ids.add(dataset_id)
                        result = dataset.copy()
                        result['similarity_score'] = float(1 / (1 + distance))
                        extended_results.append(result)
        
        # Sort by similarity and limit results
        extended_results.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        return extended_results[:num_results]