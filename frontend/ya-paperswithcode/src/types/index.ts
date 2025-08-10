export interface Paper {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  date: string;
  arxiv_id?: string;
  codeLinks?: CodeLink[];
  tags?: string[];
  trending?: boolean;
}

export interface CodeLink {
  platform: 'github' | 'gitlab' | 'bitbucket';
  url: string;
  stars?: number;
}

export interface FilterOption {
  name: string;
  count: string;
  param: string;
}

export interface DatasetFilters {
  modalities: FilterOption[];
  tasks: FilterOption[];
  languages: FilterOption[];
}

export interface MethodSubcategory {
  name: string;
  slug: string;
  methods: string[];
}

export interface MethodCategory {
  id: string;
  name: string;
  description: string;
  subcategories: MethodSubcategory[];
}

export interface Method {
  id: string;
  name: string;
  description: string;
  paper_count: number;
}

export interface Dataset {
  id: string;
  name: string;
  full_name?: string;
  description: string;
  homepage?: string;
  paper_title?: string;
  paper_url?: string;
  subtasks?: string[];
  modalities?: string[];
  languages?: string[];
  created_at?: string;
  // UI display fields (for compatibility)
  modality?: string;
  task?: string;
  size?: string;
  downloads?: number;
  papers?: number;
  thumbnail?: string;
}
