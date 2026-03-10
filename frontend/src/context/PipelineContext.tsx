import React, { createContext, useContext, useState, useEffect } from "react";
import api from "../services/api";
import type { Pipeline } from "../types";

interface PipelineContextType {
    pipelines: Pipeline[];
    selectedPipeline: Pipeline | null;
    setSelectedPipeline: (pipeline: Pipeline) => void;
    isLoading: boolean;
    error: string | null;
}

const PipelineContext = createContext<PipelineContextType | undefined>(undefined);

export const PipelineProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [pipelines, setPipelines] = useState<Pipeline[]>([]);
    const [selectedPipeline, setSelectedPipeline] = useState<Pipeline | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchPipelines = async () => {
            try {
                console.log("Fetching pipelines from:", api.defaults.baseURL + "/pipelines/");
                const response = await api.get<Pipeline[]>("/pipelines/");
                console.log("Pipelines response received:", response.status, response.data);

                if (response.data && Array.isArray(response.data)) {
                    setPipelines(response.data);
                    if (response.data.length > 0) {
                        const defaultPipeline = response.data.find((p) => p.line_number === "L5") || response.data[0];
                        setSelectedPipeline(defaultPipeline);
                    }
                } else {
                    console.error("Pipelines data is not an array:", response.data);
                    setError("Invalid pipeline data received from server");
                }
            } catch (err) {
                console.error("Failed to fetch pipelines:", err);
                setError("Failed to load pipeline configuration");
            } finally {
                setIsLoading(false);
            }
        };

        fetchPipelines();
    }, []);

    return (
        <PipelineContext.Provider
            value={{
                pipelines,
                selectedPipeline,
                setSelectedPipeline,
                isLoading,
                error,
            }}
        >
            {children}
        </PipelineContext.Provider>
    );
};

export const usePipeline = () => {
    const context = useContext(PipelineContext);
    if (context === undefined) {
        throw new Error("usePipeline must be used within a PipelineProvider");
    }
    return context;
};
