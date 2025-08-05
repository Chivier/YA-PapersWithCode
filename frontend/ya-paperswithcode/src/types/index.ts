export interface Paper {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  date: string;
  arxivId: string;
  codeLinks: CodeLink[];
  tags: string[];
  trending: boolean;
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

export interface Dataset {
  id: string;
  name: string;
  description: string;
  modality: string;
  task: string;
  size: string;
  downloads: number;
  papers: number;
  thumbnail?: string;
}