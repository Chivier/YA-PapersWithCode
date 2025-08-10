# semantic_search.py
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import faiss
from datetime import datetime

class SemanticSearchEngine:
    def __init__(self, papers: str = '', datasets: str = '', model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize semantic search engine with paper database"""
        self.model = SentenceTransformer(model_name)
        self.papers = papers
        self.datasets = datasets
        self.paper_embeddings = None
        self.dataset_embeddings = None
        self.index = None
        self.index_datasets = None
        if papers:
            self._build_index()
        if datasets:
            self._build_index_datasets()
    
    
    def _build_index(self):
        """Build FAISS index for semantic search"""
        # Create text representations for each paper
        texts = []
        for paper in self.papers:
            text = f"{paper['title']} {paper.get('abstract', '')}"
            if paper.get('tasks'):
                text += " " + " ".join(paper['tasks'])
            texts.append(text)
        
        # Generate embeddings
        print("Building embeddings for papers...")
        self.paper_embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Build FAISS index
        dimension = self.paper_embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.paper_embeddings.astype('float32'))
        print(f"Index built with {len(self.papers)} papers")
        
    def _build_index_datasets(self):
        """Build FAISS index for semantic search"""
        # Create text representations for each dataset
        texts = []
        self.nums_papers = []
        for dataset in self.datasets:
            text = f"{dataset.get('name', '')} {dataset.get('description', '')} {dataset.get('paper', '').get('title', '')}"
            text += f"tasks: {', '.join(dataset.get('tasks', []))} modalities: {', '.join(dataset.get('modalities', []))} languages: {', '.join(dataset.get('languages', []))} introduced year: {dataset.get('introduced_date', '')}"
            texts.append(text)
            num_papers = dataset.get('num_papers', 0)
            self.nums_papers.append(num_papers)
        
        
        # Generate embeddings
        print("Building embeddings for datasets...")
        self.dataset_embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Build FAISS index
        dimension = self.dataset_embeddings.shape[1]
        self.index_datasets = faiss.IndexFlatL2(dimension)
        self.index_datasets.add(self.dataset_embeddings.astype('float32'))
        print(f"Index built with {len(self.datasets)} datasets")
    
    def search_by_query_datasets(self, query: str, num_results: int = 10, end_date: Optional[str] = None) -> List[str]:
        """Search datasets by query and return dataset"""
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(query_embedding.astype('float32'), num_results * 2)
        
        candidates = []
        for rank, idx in enumerate(indices[0]):
            candidates.append({
                "d_rank": rank + 1,
                "dataset": self.datasets[idx],
                "num_papers": self.datasets[idx]["num_papers"]
            })
        candidates.sort(key=lambda c: c.get("num_papers", 0), reverse=True)
        
        k_rrf = 60.0
        gamma = 1.0
        for i, candidate in enumerate(candidates):
            candidate["p_rank"] = i + 1
            candidate["rrf_score"] = 1.0 / (k_rrf + candidate["d_rank"]) + gamma * (1.0 / (k_rrf + candidate["p_rank"]))
        top = candidates.sort(key=lambda x: x["rrf_score"], reverse=True)[:num_results]
        
        return [c["dataset"] for c in top]
    
    def extend_datasets_by_similarity(self, queries: list[Dict], galleries: list[Dict], top_k = 10):
        
        queries_text = []
        for dataset in queries:
            text = f"{dataset.get('name', '')} {dataset.get('description', '')} {dataset.get('short_description', '')}"
            queries_text.append(text)
        galleries_text = []
        for dataset in galleries:
            text = f"{dataset.get('name', '')} {dataset.get('description', '')} {dataset.get('short_description', '')}"
            galleries_text.append(text)
            
        
        query_embeddings = self.model.encode(queries_text)
        gallery_embeddings = self.model.encode(galleries_text)
        query_embeddings = query_embeddings / np.linalg.norm(query_embeddings, axis=1, keepdims=True)
        gallery_embeddings = gallery_embeddings / np.linalg.norm(gallery_embeddings, axis=1, keepdims=True)
        
        similarity_matrix = np.dot(query_embeddings, gallery_embeddings.T)
        results = []
        for i, _ in enumerate(queries):
            similarities = similarity_matrix[i]
            sorted_indices = np.argsort(similarities)[::-1] 
            filter_galleries = [galleries[idx] for idx in sorted_indices if galleries[idx] not in results]
            top_k_results = filter_galleries[:top_k]
            results.extend(top_k_results)
        return results
    
    
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