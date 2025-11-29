import axios from 'axios';

const isServer = typeof window === 'undefined';
const API_BASE_URL = isServer 
  ? 'http://backend:8000'
  : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface DocumentMetadata {
  id: string;
  filename: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  upload_date: string;
  total_sections: number;
  error_message?: string;
}

export interface Section {
  id: string;
  title: string;
  content: string;
  page_number: number;
  parent_id?: string;
  children: string[];
}

export interface Citation {
  document_id: string;
  document_name: string;
  section_id: string;
  section_title: string;
  text: string;
  score: number;
}

export interface SearchResponse {
  query: string;
  response: string;
  citations: Citation[];
}

export interface DocumentDetailResponse {
  metadata: DocumentMetadata;
  sections: Section[];
}

export const uploadDocument = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/api/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getDocuments = async (): Promise<{ documents: DocumentMetadata[] }> => {
  const response = await api.get('/api/documents');
  return response.data;
};

export const getDocument = async (documentId: string): Promise<DocumentDetailResponse> => {
  const response = await api.get(`/api/documents/${documentId}`);
  return response.data;
};

export const getSection = async (documentId: string, sectionId: string): Promise<Section> => {
  const response = await api.get(`/api/documents/${documentId}/sections/${sectionId}`);
  return response.data;
};

export const search = async (query: string): Promise<SearchResponse> => {
  const response = await api.get('/api/search', {
    params: { q: query },
  });
  return response.data;
};

export const deleteDocument = async (documentId: string) => {
  const response = await api.delete(`/api/documents/${documentId}`);
  return response.data;
};

export const resetAllDocuments = async () => {
  const response = await api.post('/api/documents/reset');
  return response.data;
};

