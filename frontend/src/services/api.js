/**
 * API service for backend communication
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class APIService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
    });
  }

  /**
   * Upload resume file
   */
  async uploadResume(file, onProgress) {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await this.client.post('/api/v1/parse', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          if (onProgress) {
            onProgress(percentCompleted);
          }
        },
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Get analysis results by job ID
   */
  async getResults(jobId) {
    try {
      const response = await this.client.get(`/api/v1/results/${jobId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Check API health
   */
  async checkHealth() {
    try {
      const response = await this.client.get('/api/v1/health');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Handle API errors
   */
  handleError(error) {
    if (error.response) {
      return {
        status: error.response.status,
        message: error.response.data.detail || 'Server error occurred',
        data: error.response.data,
      };
    } else if (error.request) {
      return {
        status: 0,
        message: 'Cannot connect to server. Please check if backend is running.',
        data: null,
      };
    } else {
      return {
        status: -1,
        message: error.message || 'An unexpected error occurred',
        data: null,
      };
    }
  }
}

export default new APIService();