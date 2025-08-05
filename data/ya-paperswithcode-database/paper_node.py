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
class PaperNode:
    def __init__(self, attrs):
        self.title        = attrs.get("title", "")
        self.arxiv_id     = attrs.get("arxiv_id", "")
        self.depth        = attrs.get("depth", -1)
        self.authors      = attrs.get('authors', [])
        self.child        = {k: [PaperNode(i) for i in v] for k, v in attrs.get("child", {}).items()}
        self.abstract     = attrs.get("abstract", "")
        self.tasks        = attrs.get("tasks", [])
        self.date         = attrs.get("date", "")
        self.select_score = attrs.get("select_score", 0.0) # the result of the selecte model
        self.extra        = attrs.get("extra", {})
        self.url_pdf      = attrs.get('url_pdf', '')
        self.url_abs      = attrs.get('url_abs', '')
        self.search_source= attrs.get('search_source', '')

    def todic(self):
        return {
            "title":        self.title,
            "arxiv_id":     self.arxiv_id,
            "depth":        self.depth,
            "authors":       self.authors,
            "child":        {k: [i.todic() for i in v] for k, v in self.child.items()},
            "abstract":     self.abstract,
            "tasks":        self.tasks,
            "date":         self.date,
            "select_score": self.select_score,
            "extra":        self.extra,
            'url_pdf':      self.url_pdf,
            'url_abs':      self.url_abs,
            'search_source':self.search_source,
        }

    @staticmethod
    def sort_paper(item):
        return item.select_score