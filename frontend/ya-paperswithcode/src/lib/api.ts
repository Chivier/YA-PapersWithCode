import axios from 'axios';
import type { Paper, Dataset, Method } from '../types';

const apiClient = axios.create({
  baseURL: 'http://0.0.0.0:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getPapers = async (page = 1, per_page = 10): Promise<{ results: Paper[], total: number }> => {
  const response = await apiClient.get('/papers', {
    params: { page, per_page },
  });
  return response.data;
};

export const getDatasets = async (
  page = 1, 
  per_page = 100,
  filters?: {
    modalities?: string[],
    languages?: string[]
  }
): Promise<{ results: Dataset[], total: number }> => {
  const params: any = { page, per_page };
  
  // Add filter parameters if provided
  if (filters) {
    if (filters.modalities && filters.modalities.length > 0) {
      params.modalities = filters.modalities.join(',');
    }
    if (filters.languages && filters.languages.length > 0) {
      params.languages = filters.languages.join(',');
    }
  }
  
  const response = await apiClient.get('/datasets', { params });
  return response.data;
};

export const getDataset = async (id: string): Promise<Dataset> => {
  const response = await apiClient.get(`/datasets/${id}`);
  return response.data;
};

export const getMethods = async (): Promise<{ results: Method[], total: number }> => {
  const response = await apiClient.get('/methods');
  return response.data;
};

export const searchPapers = async (query: string, page = 1, per_page = 10) => {
  const response = await apiClient.post('/papers/search', {
    query,
    page,
    per_page,
  });
  return response.data;
};

export const searchPapersWithAgent = async (query: string) => {
  const response = await apiClient.post('/papers/search/agent', { query });
  return response.data;
};

export const searchDatasets = async (query: string, page = 1, per_page = 10) => {
  const response = await apiClient.post('/datasets/search', {
    query,
    page,
    per_page,
  });
  return response.data;
};

export const searchDatasetsWithAgent = async (query: string) => {
  const response = await apiClient.post('/datasets/search/agent', { query });
  return response.data;
};

export const getTableCounts = async (): Promise<{ [key: string]: number }> => {
  const response = await apiClient.get('/counts');
  return response.data;
};

export const getStatistics = async () => {
  const response = await apiClient.get('/statistics');
  return response.data;
};