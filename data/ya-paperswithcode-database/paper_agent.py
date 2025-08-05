# Copyright (c) 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import re
import json
import threading
from paper_node import PaperNode
from models     import Agent
from datetime   import datetime
from utils      import (
    search_paper_by_title,
    local_search_arxiv_id,
    search_paper_by_arxiv_id,
    get_similar_papers
)

class PaperAgent:
    def __init__(
        self,
        user_query:     str,
        crawler:        Agent, # prompt(s) -> response(s)
        selector:       Agent, # prompt(s) -> score(s)
        end_date:       str = datetime.now().strftime("%Y%m%d"),
        prompts_path:   str = "agent_prompt.json",
        expand_layers:  int = 2,
        search_queries: int = 5,
        search_papers:  int = 10, # per query
        expand_papers:  int = 20, # per layer
        threads_num:    int = 20, # number of threads in parallel at the same time
    ) -> None:
        self.user_query = user_query
        self.crawler    = crawler
        self.selector   = selector
        self.end_date   = end_date
        self.prompts    = json.load(open(prompts_path))
        self.root       = PaperNode({
            "title": user_query,
            "extra": {
                "touch_ids": [],
                "crawler_recall_papers": [],
                "recall_papers": [],
            }
        })

        # hyperparameters
        self.expand_layers   = expand_layers
        self.search_queries  = search_queries
        self.search_papers   = search_papers
        self.expand_papers   = expand_papers
        self.threads_num     = threads_num
        self.papers_queue    = []
        self.expand_start    = 0
        self.lock            = threading.Lock()
        self.templates       = {
            "cite_template":   r"~\\cite\{(.*?)\}",
            "search_template": r"Search\](.*?)\[",
            "expand_template": r"Expand\](.*?)\["
        }
    
    @staticmethod
    def do_parallel(func, args, num):
        threads = []
        for _ in range(num):
            thread = threading.Thread(target=func, args=args)
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

    def search_paper(self, queries):
        while queries:
            with self.lock:
                query, self.root.child[query] = queries.pop(), []
            pre_arxiv_ids, searched_papers = local_search_arxiv_id(query, self.search_papers, self.end_date), []
            for arxiv_id in pre_arxiv_ids:
                arxiv_id = arxiv_id.split('v')[0]
                self.lock.acquire()
                if arxiv_id not in self.root.extra["touch_ids"]:
                    self.root.extra["touch_ids"].append(arxiv_id)
                    self.lock.release()
                    paper = search_paper_by_arxiv_id(arxiv_id)
                    if paper is not None:
                        searched_papers.append(paper)
                else:
                    self.lock.release()
            
            select_prompts = [self.prompts["get_selected"].format(title=paper["title"], abstract=paper["abstract"], user_query=self.user_query) for paper in searched_papers]
            scores = self.selector.infer_score(select_prompts)
            with self.lock:
                for score, paper in zip(scores, searched_papers):
                    self.root.extra["crawler_recall_papers"].append(paper["title"])
                    if score > 0.5:
                        self.root.extra["recall_papers"].append(paper["title"])
                    paper_node = PaperNode({
                        "title": paper["title"],
                        "arxiv_id": paper["arxiv_id"],
                        "depth": 0,
                        "abstract": paper["abstract"],
                        "authors": paper["authors"],
                        "tasks": paper["tasks"],
                        "date": paper["date"],
                        "url_pdf": paper["url_pdf"],
                        "url_abs": paper["url_abs"],
                        "search_source": f"Query: {query}",
                        "select_score": score,
                        "extra": {}
                    })
                    self.root.child[query].append(paper_node)
                    self.papers_queue.append(paper_node)

    def search(self):
        prompt = self.prompts["generate_query"].format(user_query=self.user_query).strip()
        queries = self.crawler.infer(prompt)
        queries = [q.strip() for q in re.findall(self.templates["search_template"], queries, flags=re.DOTALL)][:self.search_queries]
        PaperAgent.do_parallel(self.search_paper, (queries,), len(queries))

    def expand_similar_papers(self, expand_papers):
        """Expand by finding similar papers"""
        while expand_papers:
            with self.lock:
                if not expand_papers:
                    break
                paper = expand_papers.pop(0)
            
            # Get similar papers
            similar_papers = get_similar_papers(paper.arxiv_id, num=10)
            
            select_prompts = []
            valid_papers = []
            
            for similar_paper in similar_papers:
                arxiv_id = similar_paper.get("arxiv_id", "")
                if not arxiv_id:
                    continue
                    
                with self.lock:
                    if arxiv_id not in self.root.extra["touch_ids"]:
                        self.root.extra["touch_ids"].append(arxiv_id)
                        prompt = self.prompts["get_selected"].format(
                            title=similar_paper["title"], 
                            abstract=similar_paper["abstract"], 
                            user_query=self.user_query
                        )
                        select_prompts.append(prompt)
                        valid_papers.append(similar_paper)
            
            if select_prompts:
                scores = self.selector.infer_score(select_prompts)
                
                with self.lock:
                    for score, ref_paper in zip(scores, valid_papers):
                        self.root.extra["crawler_recall_papers"].append(ref_paper["title"])
                        if score > 0.5:
                            self.root.extra["recall_papers"].append(ref_paper["title"])
                        
                        paper_node = PaperNode({
                            "title": ref_paper["title"],
                            "depth": paper.depth + 1,
                            "arxiv_id": ref_paper["arxiv_id"],
                            "abstract": ref_paper["abstract"],
                            "authors": ref_paper.get("authors", []),
                            "tasks": ref_paper.get("tasks", []),
                            "date": ref_paper.get("date", ""),
                            "url_pdf": ref_paper.get("url_pdf", ""),
                            "url_abs": ref_paper.get("url_abs", ""),
                            "search_source": f"Similar to: {paper.title}",
                            "select_score": score,
                            "extra": {"similarity_score": ref_paper.get("similarity_score", 0)}
                        })
                        
                        if "similar" not in paper.child:
                            paper.child["similar"] = []
                        paper.child["similar"].append(paper_node)
                        paper.extra["expand"] = "success"
                        self.papers_queue.append(paper_node)

    def expand(self, depth):
        expand_papers = sorted(self.papers_queue[self.expand_start:], key=PaperNode.sort_paper, reverse=True)
        self.papers_queue = self.papers_queue[:self.expand_start] + expand_papers
        if depth > 0:
            expand_papers = expand_papers[:self.expand_papers]
        self.expand_start = len(self.papers_queue)
        PaperAgent.do_parallel( self.expand_similar_papers, (expand_papers,), self.threads_num)

    def run(self):
        self.search()
        for depth in range(self.expand_layers):
            self.expand(depth)
