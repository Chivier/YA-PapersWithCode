"""
Dataset Search Agent Implementation
"""
import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from .utils import get_semantic_results, init_semantic_search, extend_datasets_by_similarity

from .base import BaseSearchAgent
from .api_client import SearchAPIClient
from .models import LLM

class DatasetSearchAgent(BaseSearchAgent):
    """Agent for searching datasets with filtering and recommendation capabilities"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the dataset search agent
        
        Args:
            config: Configuration dictionary with options like:
                - data_source: 'api' or 'json'
                - search_strategy: 'basic' or 'advanced'
                - enable_filters: Whether to enable advanced filtering
                - recommend_similar: Whether to recommend similar datasets
        """
        super().__init__(config)
        
        # Dataset-specific configuration
        self.enable_filters = self.config.get('enable_filters', True)
        self.recommend_similar = self.config.get('recommend_similar', False)
        self.semantic_model_name = self.config.get('semantic_model_name', 'all-MiniLM-L6-v2')
        self.llm_model_name = self.config.get('llm_model_name', 'Qwen/Qwen2.5-7B-Instruct')
        self.query_datasets = self.config.get('query_datasets', 10)
        self.expand_datasets = self.config.get('expand_datasets', 20)
        
        # Initialize API client
        self.api_client = SearchAPIClient()
        
        all_datasets = self.api_client.get_datasets_json()
        init_semantic_search(datasets=all_datasets, model_name=self.semantic_model_name)
        self.llm = LLM(self.llm_model_name)
        self.touch_ids = []
        
        
    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Search for datasets based on query
        
        Args:
            query: Search query string
            **kwargs: Additional parameters:
                - limit: Maximum number of results
                - filters: Filter criteria (modalities, languages, etc.)
                - expand: Whether to find similar datasets
                
        Returns:
            Search results dictionary
        """
        start_time = datetime.now()
        
        limit = kwargs.get('limit', 50)
        filters = kwargs.get('filters', {})
        expand = kwargs.get('expand', False)
        
        # Get initial results based on data source
        if self.data_source == 'json':
            results = await self._search_json(query, limit, filters)
        else:
            results = await self._search_api(query, limit, filters)
        
        # Expand with similar datasets if requested
        if expand and self.recommend_similar:
            # TODO:AGENT_SEARCH - Implement dataset similarity search
            # This should:
            # 1. Find datasets with similar modalities
            # 2. Find datasets used in similar papers
            # 3. Find datasets with overlapping tasks
            # 4. Use embedding similarity for descriptions
            extend_results = self.expand_search(results)
            results.extend(extend_results)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return self.format_response(
            results=results,
            query=query,
            execution_time=execution_time,
            metadata={
                'data_source': self.data_source,
                'search_strategy': self.search_strategy,
                'filters_applied': bool(filters)
            }
        )
    
    async def _search_api(self, query: str, limit: int, filters: Dict) -> List[Dict]:
        """
        Search using database API
        
        Args:
            query: Search query
            limit: Result limit
            filters: Filter criteria
            
        Returns:
            List of dataset dictionaries
        """
        search_filters = filters.copy()
        search_filters['search'] = query
        
        return self.api_client.get_datasets(filters=search_filters, limit=limit)
    
    async def _search_json(self, query: str, limit: int, filters: Dict = {}) -> List[Dict]:
        """
        Search using JSON data
        
        Args:
            query: Search query
            limit: Result limit
            filters: Filter criteria
            
        Returns:
            List of dataset dictionaries
        """
        # Load all datasets from JSON
        
        # TODO:AGENT_SEARCH - Implement advanced dataset filtering
        # This should:
        # 1. Parse natural language queries (e.g., "image datasets with more than 10k samples")
        # 2. Apply complex filters on metadata
        # 3. Use semantic matching for descriptions
        
        
        
        parsed_query = await self._parse_query_with_llm(query)
        results = self.recommend_datasets(parsed_query)
        
        filtered_datasets = []
        
        for dataset in results:
            if filters:
                filtered_dataset = self.filter_by_characteristics([dataset], filters)
                filtered_datasets.extend(filtered_dataset)
            else:
                filtered_datasets.append(dataset)
                
        
        return filtered_datasets
    
    async def expand_search(self, initial_results: List[Dict], **kwargs) -> List[Dict]:
        """
        Find similar or related datasets
        
        Args:
            initial_results: Initial search results
            **kwargs: Expansion parameters
            
        Returns:
            Expanded search results
        """
        # TODO:AGENT_SEARCH - Implement dataset expansion
        # This should:
        # 1. Find datasets with similar characteristics
        # 2. Find datasets commonly used together
        # 3. Find dataset variants or versions
        # 4. Recommend based on task similarity
        def calculate_similarity(dataset1, dataset2):
            score = 0
            total_weight = 0
            
            if 'modalities' in dataset1 and 'modalities' in dataset2:
                mods1 = set(dataset1['modalities'])
                mods2 = set(dataset2['modalities'])
                if mods1 and mods2:
                    intersection = len(mods1.intersection(mods2))
                    union = len(mods1.union(mods2))
                    score += (intersection / union) * 2
                    total_weight += 2
                    
            if 'languages' in dataset1 and 'languages' in dataset2:
                langs1 = set(dataset1['languages'])
                langs2 = set(dataset2['languages'])
                if langs1 and langs2:
                    intersection = len(langs1.intersection(langs2))
                    union = len(langs1.union(langs2))
                    score += (intersection / union) * 1 
                    total_weight += 1

            if 'tasks' in dataset1 and 'tasks' in dataset2:
                tasks1 = [task['task'] for task in dataset1.get('tasks', [])]
                tasks2 = [task['task'] for task in dataset2.get('tasks', [])]
                if tasks1 and tasks2:
                    common_tasks = len(set(tasks1).intersection(tasks2))
                    total_tasks = len(set(tasks1).union(tasks2))
                    score += (common_tasks / total_tasks) * 2
                    total_weight += 2

            return score / total_weight if total_weight > 0 else 0

        exist_datasets = [dataset.get('id') or dataset.get('url') for dataset in initial_results]
        all_datasets = self.api_client.get_datasets_json()
        expanded_results = []
        expanded_ids = set()  # Track IDs to avoid duplicates
        
        for initial_dataset in initial_results:
            for dataset in all_datasets:
                dataset_id = dataset.get('id') or dataset.get('url')
                
                # Skip if already in results or already added
                if dataset_id in exist_datasets or dataset_id in expanded_ids:
                    continue
                    
                similarity = calculate_similarity(initial_dataset, dataset)
                if similarity >= 0.5:
                    expanded_results.append(dataset)
                    expanded_ids.add(dataset_id)
                
                # Check variants if available
                if 'variants' in initial_dataset and dataset.get('name') in initial_dataset.get('variants', []):
                    if dataset_id not in expanded_ids:
                        expanded_results.append(dataset)
                        expanded_ids.add(dataset_id)
                            
        expanded_results = extend_datasets_by_similarity(initial_results, expanded_results, self.expand_datasets)

        return expanded_results
        
    
    async def filter_by_characteristics(self, datasets: List[Dict], 
                                       characteristics: Dict[str, Any]) -> List[Dict]:
        """
        Filter datasets by specific characteristics
        
        Args:
            datasets: List of datasets to filter
            characteristics: Characteristics to filter by
            
        Returns:
            Filtered datasets
        """
        # TODO:AGENT_SEARCH - Implement characteristic-based filtering
        # This should handle:
        # 1. Number of samples
        # 2. Data modalities
        # 3. Languages
        # 4. Tasks
        # 5. Year created
        # 6. License type
        
        filtered = []
        for dataset in datasets:
            # Apply characteristic filters
            match = True
            
            if 'min_samples' in characteristics or 'max_samples' in characteristics:
                desc = dataset.get('description', '') + ' ' + dataset.get('short_description', '')
                dataset_size = self._extract_sample_size(desc)
                try:
                    if 'min_samples' in characteristics and dataset_size < characteristics['min_samples']:
                        match = False
                    if 'max_samples' in characteristics and dataset_size > characteristics['max_samples']:
                        match = False
                except:
                    match = False
            
            if 'modalities' in characteristics:
                dataset_mods = set(dataset.get('modalities', []))
                required_mods = set(characteristics['modalities'])
                if not required_mods.issubset(dataset_mods):
                    match = False
                    
            if "languages" in characteristics:
                languages = set(dataset.get('languages', []))
                required_lang = set(characteristics['languages'])
                if not required_lang.issubset(languages):
                    match = False
                    
            if 'task' in characteristics:
                tasks = [task.get('task', '') for task in dataset.get('tasks', [])]
                if not any(characteristics['task'] in task for task in tasks):
                    match = False
                    
            if 'year' in characteristics:
                intro_date = dataset.get('introduced_date', '')
                try:
                    year = int(intro_date.split('-')[0])
                    if year == characteristics['year']:
                        match = False
                except:
                    match = False
            
            if 'license_name' in characteristics:
                license_name = dataset.get('license_name', '').lower()
                if not characteristics['license_name'] in license_name:
                    match = False
                
            if match:
                filtered.append(dataset)
        
        return filtered
    
    async def recommend_datasets(self, context: Dict[str, Any]) -> List[Dict]:
        """
        Recommend datasets based on context
        
        Args:
            context: Context information (e.g., paper topic, task, etc.)
            
        Returns:
            Recommended datasets
        """
        # TODO:AGENT_SEARCH - Implement dataset recommendation
        # This should:
        # 1. Analyze the context (paper, task, etc.)
        # 2. Find commonly used datasets for the context
        # 3. Rank by relevance and popularity
        # 4. Consider dataset quality metrics
        query = context.get("raw_text", "")
        q_keywords = context.get("keywords", [])
        q_tasks = context.get("tasks", [])
        q_lang = context.get("languages", [])
        q_modal = context.get("modalities", [])
        q_min_samples = context.get("min_samples", 0)
        q_max_samples = context.get("max_samples", 1000000)
        q_introduced_year = context.get("introduced_year", 0)

        if "min_samples" in context and "max_samples" in context:
            sample_text = f"between {q_min_samples} and {q_max_samples} samples."
        elif "min_samples" in context:
            sample_text = f"at least {q_min_samples} samples."
        elif "max_samples" in context:
            sample_text = f"at most {q_max_samples} samples."
        text = query + sample_text + q_keywords + f"tasks: {', '.join(q_tasks)} modalities: {', '.join(q_modal)} languages: {', '.join(q_lang)} introduced year: {q_introduced_year}"
        
        
        results = get_semantic_results(text, self.query_datasets)
        
        
        return results
    
        
    async def _parse_query_with_llm(self, query: str) -> Dict[str, Any]:
        """
        Parse natural language query using LLM to extract structured filters
        
        Args:
            query: Natural language query
            
        Returns:
            Dictionary of extracted filters
        """
        if not self.llm:
            return {}
        
        prompt = f"""Parse the following dataset search query and extract structured filters.
        Return a JSON object containing the following fields (use `null` if a field is not present in the query):
        - keywords: List of main search keywords
        - modalities: List of data types (Images, Text, Audio, Video, Graph, Tabular, 3D)
        - tasks: List of tasks (e.g., Image Classification, Object Detection, NER, etc.)
        - languages: List of languages (e.g., English, Chinese, Multilingual)
        - min_samples: Minimum number of samples
        - max_samples: Maximum number of samples
        - introduced_year: Datasets introduced after this year
        
        Query: "{query}"
        
        Return only valid JSON without any explanation."""
        
        try:
            response = await self.llm.generate(prompt)
            filters = json.loads(response)
            
            # Validate and normalize the parsed filters
            validated_filters = {}
            
            if 'keywords' in filters:
                validated_filters['keywords'] = filters['keywords']
            
            if 'modalities' in filters:
                validated_filters['modalities'] = [m.title() for m in filters['modalities']]
            
            if 'tasks' in filters:
                validated_filters['tasks'] = [t.title() for t in filters['tasks']]
            
            if 'languages' in filters:
                validated_filters['languages'] = [l.title() for l in filters['languages']]
            
            if 'min_samples' in filters:
                validated_filters['min_samples'] = int(filters['min_samples'])
            
            if 'max_samples' in filters:
                validated_filters['max_samples'] = int(filters['max_samples'])
            
            if 'introduced_year' in filters:
                validated_filters['introduced_year'] = int(filters['introduced_year'])
            
            
            return validated_filters
            
        except Exception as e:
            print(f"Error parsing query with LLM: {e}")
            return {}
        
    def _parse_number(self, size_str: str):
        """
        Parse number strings like '10k', '1.5m', '1,000' to integers
        """
        size_str = size_str.replace(',', '')
        if size_str.endswith('k'):
            return int(float(size_str[:-1]) * 1000)
        elif size_str.endswith('m'):
            return int(float(size_str[:-1]) * 1000000)
        elif size_str.endswith('b'):
            return int(float(size_str[:-1]) * 1000000000)
        else:
            return int(size_str)
        
        
    def _extract_sample_size(self, text: str):
        """Extract sample size from dataset description"""
        text_lower = text.lower()
        
        total_patterns = [
            r'total of (\d+(?:,\d+)*(?:k|m)?)',
            r'(\d+(?:,\d+)*(?:k|m)?)\s*(?:examples|samples|instances|data points|images|texts|records|entries) in total',
            r'dataset (?:contains|has|with) (\d+(?:,\d+)*(?:k|m)?)',
            r'collection of (\d+(?:,\d+)*(?:k|m)?)',
            r'(\d+(?:,\d+)*(?:k|m)?)\s*(?:handwritten digits|images|samples)',  # 针对具体类型
        ]
        
        for pattern in total_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                try:
                    return self._parse_number(matches[0])
                except:
                    continue
        
        train_test_info = self._extract_train_test_sizes(text_lower)
        if train_test_info['total']:
            return train_test_info['total']
        
        general_patterns = [
            r'(\d+(?:,\d+)*(?:k|m)?)\s*(?:examples|samples|instances|data points|images|texts|records|entries)',
            r'(\d+(?:,\d+)*(?:k|m)?)\s*(?:training|test|validation)'
        ]
        
        sizes = []
        for pattern in general_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                try:
                    sizes.append(self._parse_number(match))
                except:
                    pass
        
        return max(sizes) if sizes else None

    def _extract_train_test_sizes(self, text: str):
        """Extract training and test set sizes separately"""
        result = {
            'train': None,
            'test': None,
            'validation': None,
            'total': None
        }
        
        # 训练集模式
        train_patterns = [
            r'training set of (\d+(?:,\d+)*(?:k|m)?)',
            r'train set of (\d+(?:,\d+)*(?:k|m)?)',
            r'(\d+(?:,\d+)*(?:k|m)?)\s*training',
            r'train.*?(\d+(?:,\d+)*(?:k|m)?)'
        ]
        
        # 测试集模式
        test_patterns = [
            r'test set of (\d+(?:,\d+)*(?:k|m)?)',
            r'(\d+(?:,\d+)*(?:k|m)?)\s*test',
            r'test.*?(\d+(?:,\d+)*(?:k|m)?)'
        ]
        
        # 验证集模式
        val_patterns = [
            r'validation set of (\d+(?:,\d+)*(?:k|m)?)',
            r'(\d+(?:,\d+)*(?:k|m)?)\s*validation',
            r'val.*?(\d+(?:,\d+)*(?:k|m)?)'
        ]
        
        # 提取各个数据集大小
        for patterns, key in [(train_patterns, 'train'), (test_patterns, 'test'), (val_patterns, 'validation')]:
            for pattern in patterns:
                matches = re.findall(pattern, text)
                if matches:
                    try:
                        result[key] = self._parse_number(matches[0])
                        break
                    except:
                        continue
        
        # 计算总数
        sizes = [size for size in result.values() if size is not None and size > 0]
        if len(sizes) >= 2:  # 至少有训练集和测试集
            result['total'] = sum(sizes)
        
        return result
