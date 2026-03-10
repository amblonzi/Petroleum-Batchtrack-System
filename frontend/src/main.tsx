import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import axios from "axios";
import { PipelineProvider } from "./context/PipelineContext";

// Set base URL for axios
const apiUrl = import.meta.env.VITE_API_URL || "/api";
axios.defaults.baseURL = apiUrl;

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <PipelineProvider>
        <App />
      </PipelineProvider>
    </QueryClientProvider>
  </React.StrictMode>
);
