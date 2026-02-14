import axios from "axios";

const isDev = import.meta.env.DEV;

const api = axios.create({
  baseURL: isDev
    ? "http://localhost:8000"
    : "https://api.xergiz.com/text-hunter",
  headers: { "Content-Type": "application/json" },
});

export default api;

