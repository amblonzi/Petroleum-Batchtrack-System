
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "../services/api";
import type { FlowEntry, Station } from "../types";
import { usePipeline } from "../context/PipelineContext";

interface HistoryPaneProps {
  stations: Station[];
}

export default function HistoryPane({ stations }: HistoryPaneProps) {
  const [activeTab, setActiveTab] = useState<"lifting" | "receiving">("lifting");
  const { selectedPipeline } = usePipeline();

  // Identify station IDs
  const liftingStation = stations.find((s) => s.station_type === "lifting");
  const receivingStations = stations.filter((s) => s.station_type === "receiving");
  const receivingIds = receivingStations.map((s) => s.id);

  const { data: history } = useQuery<FlowEntry[]>({
    queryKey: ["flow-history", activeTab, selectedPipeline?.line_number],
    queryFn: async () => {
      if (!selectedPipeline) return null;
      const params = new URLSearchParams();
      params.append("limit", "50");
      params.append("line", selectedPipeline.line_number);

      if (activeTab === "lifting") {
        if (liftingStation) params.append("station_id", liftingStation.id.toString());
      }

      const res = await api.get(`/flow-entries/history?${params.toString()}`);
      return res.data;
    },
    refetchInterval: 5000,
    enabled: !!selectedPipeline,
  });

  const filteredHistory = history?.filter((entry) => {
    if (activeTab === "lifting") {
      return entry.station_id === liftingStation?.id;
    } else {
      return receivingIds.includes(entry.station_id);
    }
  });

  return (
    <div className="bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-700 h-[500px] flex flex-col">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <span>📜</span> Flow History
      </h3>

      {/* Tabs */}
      <div className="flex gap-2 mb-4 bg-gray-900 p-1 rounded-lg">
        <button
          onClick={() => setActiveTab("lifting")}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-bold transition-colors ${activeTab === "lifting"
              ? "bg-blue-600 text-white shadow"
              : "text-gray-400 hover:text-white hover:bg-gray-800"
            }`}
        >
          Lifting
        </button>
        <button
          onClick={() => setActiveTab("receiving")}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-bold transition-colors ${activeTab === "receiving"
              ? "bg-green-600 text-white shadow"
              : "text-gray-400 hover:text-white hover:bg-gray-800"
            }`}
        >
          Receiving
        </button>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto pr-2 space-y-2 custom-scrollbar">
        {filteredHistory?.length === 0 && (
          <div className="text-center text-gray-500 py-8">
            No records found.
          </div>
        )}

        {filteredHistory?.map((entry) => {
          const station = stations.find((s) => s.id === entry.station_id);
          return (
            <div
              key={entry.id}
              className="bg-gray-900/50 p-3 rounded border border-gray-700 flex justify-between items-center"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${station?.station_type === "lifting" ? "bg-blue-900 text-blue-200" : "bg-green-900 text-green-200"
                    }`}>
                    {station?.code}
                  </span>
                  <span className="text-gray-300 text-sm font-medium">
                    {new Date(entry.entry_time).toLocaleString()}
                  </span>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Batch ID: {entry.batch_id}
                </div>
              </div>
              <div className="text-right">
                <div className="text-white font-bold">
                  {entry.hourly_volume.toLocaleString()} m³
                </div>
                <div className="text-[10px] text-gray-400">
                  Hourly Rate
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
