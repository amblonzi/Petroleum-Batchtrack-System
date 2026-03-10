import { useQuery } from "@tanstack/react-query";
import api from "../services/api";
import { usePipeline } from "../context/PipelineContext";
import type { Batch } from "../types";

export default function GainLoss() {
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

    // Filter only batches that have started or finished (where gain/loss is relevant)
    const activeBatches = batches?.filter(b => b.pumped_volume > 0) || [];

    const totalPumped = activeBatches.reduce((acc, b) => acc + b.pumped_volume, 0);
    const totalReceived = activeBatches.reduce((acc, b) => acc + b.received_volume, 0);
    const netVariance = totalReceived - totalPumped;

    return (
        <div className="p-6 h-full flex flex-col space-y-6 overflow-hidden">
            <div className="flex justify-between items-end">
                <div>
                    <h2 className="text-3xl font-black text-white tracking-tighter uppercase">Gain / Loss Accounting</h2>
                    <p className="text-gray-400 font-medium">Volumetric balancing for {selectedPipeline?.line_number}</p>
                </div>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700 shadow-xl">
                    <p className="text-xs font-black text-gray-500 uppercase tracking-widest mb-1">Total Intake (Pumped)</p>
                    <p className="text-3xl font-black text-blue-400 font-mono">{totalPumped.toLocaleString()} <span className="text-sm">m³</span></p>
                </div>
                <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700 shadow-xl">
                    <p className="text-xs font-black text-gray-500 uppercase tracking-widest mb-1">Total Outturn (Received)</p>
                    <p className="text-3xl font-black text-green-400 font-mono">{totalReceived.toLocaleString()} <span className="text-sm">m³</span></p>
                </div>
                <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700 shadow-xl">
                    <p className="text-xs font-black text-gray-500 uppercase tracking-widest mb-1">Net Variance</p>
                    <p className={`text-3xl font-black font-mono ${netVariance >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {netVariance >= 0 ? '+' : ''}{netVariance.toLocaleString()} <span className="text-sm">m³</span>
                    </p>
                </div>
            </div>

            <div className="bg-gray-800 rounded-2xl border border-gray-700 overflow-hidden shadow-2xl flex-1 flex flex-col min-h-0">
                <div className="overflow-y-auto custom-scrollbar">
                    <table className="w-full text-left border-collapse">
                        <thead className="sticky top-0 bg-gray-800 z-10">
                            <tr className="border-b border-gray-700">
                                <th className="px-6 py-4 text-xs font-black text-gray-500 uppercase tracking-widest">Batch Info</th>
                                <th className="px-6 py-4 text-xs font-black text-gray-500 uppercase tracking-widest text-right">Intake (m³)</th>
                                <th className="px-6 py-4 text-xs font-black text-gray-500 uppercase tracking-widest text-right">Outturn (m³)</th>
                                <th className="px-6 py-4 text-xs font-black text-gray-500 uppercase tracking-widest text-right">Variance (m³)</th>
                                <th className="px-6 py-4 text-xs font-black text-gray-500 uppercase tracking-widest text-center">Efficiency %</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-700/50">
                            {activeBatches.map((batch) => {
                                const variance = batch.received_volume - batch.pumped_volume;
                                const efficiency = batch.pumped_volume > 0 ? (batch.received_volume / batch.pumped_volume) * 100 : 0;

                                return (
                                    <tr key={batch.id} className="hover:bg-gray-750/50 transition-colors">
                                        <td className="px-6 py-4">
                                            <div className="flex flex-col">
                                                <span className="font-black text-white font-mono">{batch.name}</span>
                                                <div className="flex items-center gap-1.5 mt-1">
                                                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: batch.product?.color }} />
                                                    <span className="text-xs text-gray-400 font-bold uppercase">{batch.product?.name}</span>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-right font-black text-blue-400 font-mono italic">
                                            {batch.pumped_volume.toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4 text-right font-black text-green-400 font-mono">
                                            {batch.received_volume.toLocaleString()}
                                        </td>
                                        <td className={`px-6 py-4 text-right font-black font-mono ${variance >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                            {variance >= 0 ? '+' : ''}{variance.toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4 text-center">
                                            <span className={`px-2 py-1 rounded-full text-[10px] font-black tracking-tighter ${efficiency >= 99.5 ? 'bg-green-500/10 text-green-500 border border-green-500/20' :
                                                    'bg-red-500/10 text-red-500 border border-red-500/20'
                                                }`}>
                                                {efficiency.toFixed(2)}%
                                            </span>
                                        </td>
                                    </tr>
                                );
                            })}
                            {activeBatches.length === 0 && (
                                <tr>
                                    <td colSpan={5} className="px-6 py-20 text-center text-gray-500 italic font-medium">
                                        No active or completed batches to calculate gain/loss metrics.
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
