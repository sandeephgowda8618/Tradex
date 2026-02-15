import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
});

export const createAnalysis = (symbol, selectedFundamentals, selectedTechnicals) => {
  const params = new URLSearchParams();
  params.set("symbol", symbol);
  if (selectedFundamentals?.length) {
    selectedFundamentals.forEach((f) => params.append("selected_fundamentals", f));
  }
  if (selectedTechnicals?.length) {
    selectedTechnicals.forEach((t) => params.append("selected_technicals", t));
  }
  return API.post(`/analysis/?${params.toString()}`);
};

export const getAnalysis = (analysisId) => API.get(`/analysis/${analysisId}`);
