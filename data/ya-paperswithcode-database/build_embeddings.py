#!/usr/bin/env python3
"""
Pre-build embeddings for datasets and papers to avoid memory issues during runtime
"""
import json
import pickle
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import torch
import gc

def build_dataset_embeddings(datasets_file='datasets.json', output_file='embeddings/datasets_embeddings.pkl'):
    """Build and save dataset embeddings"""
    print("Building dataset embeddings...")
    
    # Create output directory
    Path(output_file).parent.mkdir(exist_ok=True)
    
    # Load datasets
    print(f"Loading datasets from {datasets_file}...")
    with open(datasets_file, 'r') as f:
        datasets = json.load(f)
    print(f"Loaded {len(datasets)} datasets")
    
    # Initialize model on CPU to avoid GPU memory issues
    print("Loading sentence transformer model (CPU only)...")
    device = torch.device('cpu')
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device=device)
    
    # Create text representations
    texts = []
    for item in datasets:
        text = f"{item.get('name', '')} {item.get('full_name', '')} {item.get('description', '')}"
        if item.get('modalities'):
            text += " " + " ".join(item.get('modalities', []))
        if item.get('languages'):
            text += " " + " ".join(item.get('languages', []))
        texts.append(text)
    
    # Generate embeddings in batches to save memory
    print("Generating embeddings...")
    batch_size = 32
    embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_embeddings = model.encode(batch, show_progress_bar=False)
        embeddings.extend(batch_embeddings)
        
        # Progress indicator
        if i % 1000 == 0:
            print(f"  Processed {i}/{len(texts)} datasets...")
    
    embeddings = np.array(embeddings)
    print(f"Generated embeddings with shape: {embeddings.shape}")
    
    # Build FAISS index
    print("Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype('float32'))
    
    # Save embeddings and index
    print(f"Saving to {output_file}...")
    with open(output_file, 'wb') as f:
        pickle.dump({
            'embeddings': embeddings,
            'datasets': datasets,
            'dimension': dimension
        }, f)
    
    # Also save FAISS index separately
    faiss_file = output_file.replace('.pkl', '.faiss')
    faiss.write_index(index, faiss_file)
    print(f"Saved FAISS index to {faiss_file}")
    
    # Clean up to free memory
    del model
    del embeddings
    del index
    torch.cuda.empty_cache()
    gc.collect()
    
    print("✓ Dataset embeddings built successfully!")
    return True

def build_paper_embeddings(papers_file='papers-with-abstracts.json', output_file='embeddings/papers_embeddings.pkl'):
    """Build and save paper embeddings"""
    print("Building paper embeddings...")
    
    # Create output directory
    Path(output_file).parent.mkdir(exist_ok=True)
    
    # Load papers
    print(f"Loading papers from {papers_file}...")
    with open(papers_file, 'r') as f:
        papers = json.load(f)
    print(f"Loaded {len(papers)} papers")
    
    # Initialize model on CPU to avoid GPU memory issues
    print("Loading sentence transformer model (CPU only)...")
    device = torch.device('cpu')
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device=device)
    
    # Create text representations
    texts = []
    for paper in papers:
        text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
        if paper.get('tasks'):
            text += " " + " ".join(paper.get('tasks', []))
        texts.append(text)
    
    # Generate embeddings in batches
    print("Generating embeddings...")
    batch_size = 32
    embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_embeddings = model.encode(batch, show_progress_bar=False)
        embeddings.extend(batch_embeddings)
        
        # Progress indicator
        if i % 5000 == 0:
            print(f"  Processed {i}/{len(texts)} papers...")
    
    embeddings = np.array(embeddings)
    print(f"Generated embeddings with shape: {embeddings.shape}")
    
    # Build FAISS index
    print("Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype('float32'))
    
    # Save embeddings and index
    print(f"Saving to {output_file}...")
    with open(output_file, 'wb') as f:
        pickle.dump({
            'embeddings': embeddings,
            'papers': papers,
            'dimension': dimension
        }, f)
    
    # Also save FAISS index separately
    faiss_file = output_file.replace('.pkl', '.faiss')
    faiss.write_index(index, faiss_file)
    print(f"Saved FAISS index to {faiss_file}")
    
    # Clean up to free memory
    del model
    del embeddings
    del index
    torch.cuda.empty_cache()
    gc.collect()
    
    print("✓ Paper embeddings built successfully!")
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--papers':
        build_paper_embeddings()
    elif len(sys.argv) > 1 and sys.argv[1] == '--datasets':
        build_dataset_embeddings()
    else:
        # Build both by default
        print("Building embeddings for datasets and papers...")
        print("=" * 60)
        build_dataset_embeddings()
        print()
        print("=" * 60)
        # Optionally build paper embeddings if needed
        # build_paper_embeddings()
        
    print("\n✓ All embeddings built successfully!")
    print("You can now start the backend server.")