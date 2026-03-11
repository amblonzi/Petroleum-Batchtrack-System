import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../services/api";
import type { Batch } from "../types";
import { usePipeline } from "../context/PipelineContext";
import EditBatchModal from "./EditBatchModal";

export default function LiveBatchesPane() {
    const { selectedPipeline } = usePipeline();
    const queryClient = useQueryClient();
    const [editingBatch, setEditingBatch] = useState<Batch | null>(null);

    const { data: batches, isLoading } = useQuery<Batch[]>({
        queryKey: ["batches", selectedPipeline?.line_number],
        queryFn: () => api.get(`/batches/?line=${selectedPipeline?.line_number}`).then((r) => r.data),
        refetchInterval: 5000,
        enabled: !!selectedPipeline,
    });

    const deleteMutation = useMutation({
        mutationFn: (batchId: number) => api.delete(`/batches/${batchId}`),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["batches"] });
        },
    });

    const handleDelete = (batchId: number, batchName: string) => {
        if (window.confirm(`Are you sure you want to delete batch "${batchName}"?`)) {
            deleteMutation.mutate(batchId);
        }
    };

    const liveBatches = batches?.filter((b) => b.status === "CREATED" || b.status === "PUMPING") || [];

    if (isLoading) return <div className="text-gray-400 p-4">Loading live batches...</div>;

    return (
        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden flex flex-col h-full shadow-xl">
            <div className="bg-gray-750 px-5 py-3 border-b border-gray-700 flex justify-between items-center">
                <h3 className="text-sm font-black text-gray-300 uppercase tracking-widest">Live Batches</h3>
                <span className="bg-blue-600/20 text-blue-400 text-[10px] font-bold px-2 py-0.5 rounded-full border border-blue-500/30">
                    {liveBatches.length} Active
                </span>
            </div>

            <div className="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-2">
                {liveBatches.length === 0 ? (
                    <div className="text-center py-8">
                        <p className="text-gray-500 text-xs font-bold uppercase tracking-tighter">No live batches</p>
                    </div>
                ) : (
                    liveBatches.map((batch) => (
                        <div
                            key={batch.id}
                            className="bg-gray-900/50 border border-gray-700/50 rounded-lg p-3 hover:border-gray-600 transition-colors group relative overflow-hidden"
                        >
                            {/* Product Color Strip */}
                            <div
                                className="absolute left-0 top-0 bottom-0 w-1"
                                style={{ backgroundColor: batch.product?.color || '#4B5563' }}
                            />

                            <div className="flex justify-between items-start mb-1">
                                <div className="flex flex-col min-w-0">
                                    <h4 className="font-bold text-white text-sm truncate">{batch.name}</h4>
                                    <span className="text-[10px] text-gray-500 font-medium">{batch.product?.name || 'Unknown'}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className={`text-[9px] font-black px-1.5 py-0.5 rounded uppercase tracking-tighter ${batch.status === 'PUMPING'
                                            ? 'bg-green-500/10 text-green-500 border border-green-500/20 animate-pulse'
                                            : 'bg-yellow-500/10 text-yellow-500 border border-yellow-500/20'
                                        }`}>
                                        {batch.status}
                                    </span>
                                    {batch.status === 'CREATED' && (
                                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <button
                                                onClick={() => setEditingBatch(batch)}
                                                className="p-1 hover:bg-gray-700 rounded text-blue-400"
                                                title="Edit Batch"
                                            >
                                                <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                                                    <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                                                </svg>
                                            </button>
                                            <button
                                                onClick={() => handleDelete(batch.id, batch.name)}
                                                className="p-1 hover:bg-gray-700 rounded text-red-400"
                                                title="Delete Batch"
                                            >
                                                <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                                                    <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                                                </svg>
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </div>

                            <div className="grid grid-cols-3 gap-2 text-[10px] mt-2">
                                <div className="flex flex-col">
                                    <span className="text-gray-500 font-bold uppercase tracking-tighter">Total</span>
                                    <span className="text-gray-300 font-mono">{batch.total_volume.toLocaleString()}</span>
                                </div>
                                <div className="flex flex-col items-center">
                                    <span className="text-gray-500 font-bold uppercase tracking-tighter">Pumped</span>
                                    <span className="text-blue-400 font-mono">{batch.pumped_volume.toLocaleString()}</span>
                                </div>
                                <div className="flex flex-col items-end">
                                    <span className="text-gray-500 font-bold uppercase tracking-tighter">Balance</span>
                                    <span className="text-white font-mono">{(batch.total_volume - batch.pumped_volume).toLocaleString()}</span>
                                </div>
                            </div>

                            {batch.status === 'PUMPING' && (
                                <div className="mt-2 h-1 w-full bg-gray-800 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-green-500 transition-all duration-1000"
                                        style={{ width: `${(batch.pumped_volume / batch.total_volume) * 100}%` }}
                                    />
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>

            {editingBatch && (
                <EditBatchModal
                    batch={editingBatch}
                    onClose={() => setEditingBatch(null)}
                />
            )}
        </div>
    );
}
