import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import type { Station } from "../types";

interface VisualizationData {
  batches: Array<{
    batch_id: number;
    batch_name: string;
    product_name: string;
    color: string;
    leading_edge_km: number;
    trailing_edge_km: number;
    receiving: boolean;
    received_volume: number;
  }>;
  stations: (Station & { cumulative_volume: number; received_volume: number })[];
}

const RECEIVING_STATIONS = ["PS8", "PS9", "PS10"];

export default function ReceivingOperations() {
  const [selectedStationCode, setSelectedStationCode] = useState<string>("");
  const [volume, setVolume] = useState("");
  const queryClient = useQueryClient();

  // Fetch visualization data to know what's available
  const { data: viz } = useQuery<VisualizationData>({
    queryKey: ["visualization"],
    queryFn: async () => {
      const res = await axios.get("/api/visualization/current");
      return res.data;
    },
    refetchInterval: 5000,
  });

  const mutation = useMutation({
    mutationFn: (data: { batch_id: number; station_id: number; hourly_volume: number; entry_time: string }) => {
      return axios.post("/api/flow-entries/", data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["visualization"] });
      setVolume("");
      alert("Product received successfully!");
    },
    onError: (err) => {
      alert("Error receiving product: " + err);
    },
  });

  const selectedStation = viz?.stations.find((s) => s.code === selectedStationCode);

  // Find batches currently at the selected station
  const availableBatches = viz?.batches.filter((b) => {
    if (!selectedStation) return false;
    // Check if station KM is within batch range
    return (
      b.leading_edge_km >= selectedStation.kilometer_post &&
      b.trailing_edge_km <= selectedStation.kilometer_post
    );
  });

  const activeBatch = availableBatches && availableBatches.length > 0 ? availableBatches[0] : null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedStation || !activeBatch || !volume) return;

    mutation.mutate({
      batch_id: activeBatch.batch_id,
      station_id: selectedStation.id,
      hourly_volume: parseFloat(volume),
      entry_time: new Date().toISOString(),
    });
  };

  return (
    <div className="bg-gray-900 p-6 rounded-xl mt-6">
      <h2 className="text-2xl font-bold text-white mb-6">Receiving Operations</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Receiving Station</label>
            <select
              value={selectedStationCode}
              onChange={(e) => setSelectedStationCode(e.target.value)}
              className="w-full bg-gray-800 text-white rounded px-3 py-2 border border-gray-600 focus:border-blue-500 focus:outline-none"
              required
            >
              <option value="">Select Station...</option>
              {RECEIVING_STATIONS.map((code) => (
                <option key={code} value={code}>
                  {code}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">Product / Batch</label>
            <div className="w-full bg-gray-800 text-white rounded px-3 py-2 border border-gray-600 min-h-[42px] flex items-center">
              {activeBatch ? (
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: activeBatch.color }}
                  ></div>
                  <span>{activeBatch.product_name}</span>
                  <span className="text-gray-500 text-xs">({activeBatch.batch_name})</span>
                </div>
              ) : (
                <span className="text-gray-500 italic">
                  {selectedStationCode ? "No product at station" : "Select a station first"}
                </span>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">Volume to Receive (m³)</label>
            <input
              type="number"
              value={volume}
              onChange={(e) => setVolume(e.target.value)}
              className="w-full bg-gray-800 text-white rounded px-3 py-2 border border-gray-600 focus:border-blue-500 focus:outline-none"
              placeholder="Enter volume..."
              required
              min="0.1"
              step="0.1"
              disabled={!activeBatch}
            />
          </div>

          <button
            type="submit"
            disabled={!activeBatch || mutation.isPending}
            className="w-full py-3 bg-blue-600 text-white rounded font-bold hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {mutation.isPending ? "Processing..." : "Receive Product"}
          </button>
        </form>

        {/* Status / Info Panel */}
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-lg font-bold text-white mb-4">Current Status</h3>
          
          {selectedStation && activeBatch ? (
            <div className="space-y-4">
              <div className="flex justify-between items-center pb-2 border-b border-gray-700">
                <span className="text-gray-400">Station</span>
                <span className="text-white font-mono">{selectedStation.code}</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-gray-700">
                <span className="text-gray-400">Current Product</span>
                <span className="text-white font-bold" style={{ color: activeBatch.color }}>
                  {activeBatch.product_name}
                </span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-gray-700">
                <span className="text-gray-400">Batch Name</span>
                <span className="text-white font-mono text-sm">{activeBatch.batch_name}</span>
              </div>
              
              <div className="mt-6">
                <div className="text-sm text-gray-400 mb-1">Cumulative Received (This Batch)</div>
                <div className="text-3xl font-bold text-green-400 font-mono">
                  {activeBatch.received_volume.toLocaleString()} <span className="text-lg text-gray-500">m³</span>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Total volume received for this specific batch at all receiving stations.
                </p>
              </div>
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-gray-500">
              <p>Select a station with an active batch to view details.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
