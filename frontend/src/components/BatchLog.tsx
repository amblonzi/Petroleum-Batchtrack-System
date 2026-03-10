import { useQuery } from "@tanstack/react-query";
import api from "../services/api";
import { usePipeline } from "../context/PipelineContext";
import type { Batch } from "../types";

export default function BatchLog() {
    const { selectedPipeline } = usePipeline();

    const { data: batches, isLoading } = useQuery<Batch[]>({
        queryKey: ["batches", selectedPipeline?.line_number],
        queryFn: () => api.get(`/batches/?line=${selectedPipeline?.line_number}`).then((r) => r.data),
        enabled: !!selectedPipeline,
        refetchInterval: 10000,
    });

    if (isLoading) {
        return (
            <div className="flex items-center justify-center p-20">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    return (
        <div className="p-6 h-full flex flex-col space-y-6 overflow-hidden">
            <div className="flex justify-between items-end">
                <div>
                    <h2 className="text-3xl font-black text-white tracking-tighter uppercase">Batch Logs</h2>
                    <p className="text-gray-400 font-medium">Historical record of all pumping operations for {selectedPipeline?.line_number}</p>
                </div>
                <div className="bg-gray-800 px-4 py-2 rounded-lg border border-gray-700">
                    <span className="text-xs font-black text-gray-500 uppercase tracking-widest mr-2">Total Batches</span>
                    <span className="text-xl font-black text-blue-400 font-mono">{batches?.length || 0}</span>
                </div>
            </div>

            <div className="bg-gray-800 rounded-2xl border border-gray-700 overflow-hidden shadow-2xl flex-1 flex flex-col min-h-0">
                <div className="overflow-y-auto custom-scrollbar">
                    <table className="w-full text-left border-collapse">
                        <thead className="sticky top-0 bg-gray-800 z-10">
                            <tr className="border-b border-gray-700">
                                <th className="px-6 py-4 text-xs font-black text-gray-500 uppercase tracking-widest">Status</th>
                                <th className="px-6 py-4 text-xs font-black text-gray-500 uppercase tracking-widest">Batch Name</th>
                                <th className="px-6 py-4 text-xs font-black text-gray-500 uppercase tracking-widest">Product</th>
                                <th className="px-6 py-4 text-xs font-black text-gray-500 uppercase tracking-widest text-right">Target (m³)</th>
                                <th className="px-6 py-4 text-xs font-black text-gray-500 uppercase tracking-widest text-right">Pumped (m³)</th>
                                <th className="px-6 py-4 text-xs font-black text-gray-500 uppercase tracking-widest text-right">Received (m³)</th>
                                <th className="px-6 py-4 text-xs font-black text-gray-500 uppercase tracking-widest">Timeline</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-700/50">
                            {batches?.map((batch) => (
                                <tr key={batch.id} className="hover:bg-gray-750/50 transition-colors group">
                                    <td className="px-6 py-4">
                                        <span className={`px-2 py-1 rounded text-[10px] font-black uppercase tracking-tighter shadow-sm ${batch.status === 'COMPLETED' ? 'bg-green-500/10 text-green-500 border border-green-500/20' :
                                                batch.status === 'PUMPING' ? 'bg-blue-500/10 text-blue-500 border border-blue-500/20 animate-pulse' :
                                                    'bg-gray-500/10 text-gray-400 border border-gray-500/20'
                                            }`}>
                                            {batch.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 font-black text-white font-mono">{batch.name}</td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-2">
                                            <div className="w-2 h-2 rounded-full shadow-lg" style={{ backgroundColor: batch.product?.color }} />
                                            <span className="font-bold text-gray-200">{batch.product?.name}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-right font-black text-gray-400 font-mono italic">
                                        {batch.total_volume.toLocaleString()}
                                    </td>
                                    <td className="px-6 py-4 text-right font-black text-blue-400 font-mono">
                                        {batch.pumped_volume.toLocaleString()}
                                    </td>
                                    <td className="px-6 py-4 text-right font-black text-green-400 font-mono">
                                        {batch.received_volume.toLocaleString()}
                                    </td>
                                    <td className="px-6 py-4 text-xs text-gray-500 font-medium">
                                        {batch.started_pumping_at ? (
                                            <div className="flex flex-col">
                                                <span className="text-gray-400">IN: {new Date(batch.started_pumping_at).toLocaleString()}</span>
                                                {batch.finished_pumping_at && (
                                                    <span className="text-gray-500">OUT: {new Date(batch.finished_pumping_at).toLocaleString()}</span>
                                                )}
                                            </div>
                                        ) : (
                                            <span className="italic">Not started</span>
                                        )}
                                    </td>
                                </tr>
                            ))}
                            {batches?.length === 0 && (
                                <tr>
                                    <td colSpan={7} className="px-6 py-20 text-center text-gray-500 italic font-medium">
                                        No batches recorded for this pipeline yet.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
