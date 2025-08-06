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

export const getDatasets = async (page = 1, per_page = 100): Promise<{ results: Dataset[], total: number }> => {
  const response = await apiClient.get('/datasets', {
    params: { page, per_page },
  });
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
  const response = await apiClient.post('/search/sqlite', {
    query,
    page,
    per_page,
  });
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