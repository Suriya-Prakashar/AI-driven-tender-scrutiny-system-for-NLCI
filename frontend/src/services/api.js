import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const apiService = {
  // File management APIs
  getFiles: async () => {
    const response = await apiClient.get("/files");
    return response.data;
  },

  uploadFiles: async (files) => {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append("files", files[i]);
    }
    const response = await apiClient.post("/files/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  clearFiles: async () => {
    const response = await apiClient.post("/files/clear");
    return response.data;
  },

  deleteFile: async (filename) => {
    const response = await apiClient.delete(`/files/${encodeURIComponent(filename)}`);
    return response.data;
  },

  getDownloadUrl: (filename) => {
    return `${API_BASE_URL}/files/${encodeURIComponent(filename)}/download`;
  },

  // Merge APIs
  mergeFiles: async (files, mergedFilename) => {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append("files", files[i]);
    }
    if (mergedFilename) {
      formData.append("merged_filename", mergedFilename);
    }
    const response = await apiClient.post("/merge", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  // Evaluation / Scrutiny APIs
  startEvaluation: async (files) => {
    const response = await apiClient.post("/workflow/start", { files });
    return response.data;
  },

  getEvaluationStatus: async (jobId) => {
    const response = await apiClient.get(`/workflow/status/${jobId}`);
    return response.data;
  },

  // Udyam Verification APIs
  verifyUdyam: async (mode = "webhook", files = null, excelPath = null) => {
    const payload = { mode };
    if (files) payload.files = files;
    if (excelPath) payload.excel_path = excelPath;
    
    const response = await apiClient.post("/udyam/verify", payload);
    return response.data;
  },

  getUdyamStatus: async (jobId) => {
    const response = await apiClient.get(`/udyam/status/${jobId}`);
    return response.data;
  },
};
