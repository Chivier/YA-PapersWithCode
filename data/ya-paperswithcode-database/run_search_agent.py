import os
import json
import argparse
from models      import Agent
from paper_agent import PaperAgent
from datetime    import datetime, timedelta
from utils import init_semantic_search


parser = argparse.ArgumentParser()
parser.add_argument('--papers_file', type=str, default="papers.json", help="Path to papers JSON file")
parser.add_argument('--input_file',     type=str, default="data/RealScholarQuery/test.jsonl")
parser.add_argument('--crawler_path',   type=str, default="checkpoints/pasa-7b-crawler")
parser.add_argument('--selector_path',  type=str, default="checkpoints/pasa-7b-selector")
parser.add_argument('--output_folder',  type=str, default="results")
parser.add_argument('--expand_layers',  type=int, default=2)
parser.add_argument('--search_queries', type=int, default=5)
parser.add_argument('--search_papers',  type=int, default=10)
parser.add_argument('--expand_papers',  type=int, default=20)
parser.add_argument('--threads_num',    type=int, default=20)
args = parser.parse_args()

# Initialize semantic search engine
print(f"Loading papers from {args.papers_file}...")
init_semantic_search(args.papers_file)

crawler = Agent(args.crawler_path)
selector = Agent(args.selector_path)

with open(args.input_file) as f:
    for idx, line in enumerate(f.readlines()):
        data = json.loads(line)
        end_date = datetime.now().strftime("%Y%m%d")
        if 'source_meta' in data and 'published_time' in data['source_meta']:
            end_date = data['source_meta']['published_time']
            end_date = datetime.strptime(end_date, "%Y%m%d") - timedelta(days=7)
            end_date = end_date.strftime("%Y%m%d")
        paper_agent = PaperAgent(
            user_query     = data['question'], 
            crawler        = crawler,
            selector       = selector,
            end_date       = end_date,
            expand_layers  = args.expand_layers,
            search_queries = args.expand_papers,
            search_papers  = args.search_papers,
            expand_papers  = args.expand_papers,
            threads_num    = args.threads_num
        )
        if "answer" in data:
            paper_agent.root.extra["answer"] = data["answer"]
        
        paper_agent.run()
        
        if args.output_folder != "":
            json.dump(paper_agent.root.todic(), open(os.path.join(args.output_folder, f"{idx}.json"), "w"), indent=2)