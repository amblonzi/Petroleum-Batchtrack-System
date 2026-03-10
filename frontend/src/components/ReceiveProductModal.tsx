import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import type { Station } from "../types";

interface ReceiveProductModalProps {
  station: Station;
  activeBatch: {
    batch_id: number;
    batch_name: string;
    product_name: string;
  } | null;
  onClose: () => void;
}

export default function ReceiveProductModal({ station, activeBatch, onClose }: ReceiveProductModalProps) {
  const [volume, setVolume] = useState("");
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (data: { batch_id: number; station_id: number; hourly_volume: number; entry_time: string }) => {
      return axios.post("/flow-entries/", data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["visualization"] });
      queryClient.invalidateQueries({ queryKey: ["batches"] });
      onClose();
      alert(`Successfully received product at ${station.code}!`);
    },
    onError: (err) => {
      alert("Error receiving product: " + err);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeBatch || !volume) return;

    mutation.mutate({
      batch_id: activeBatch.batch_id,
      station_id: station.id,
      hourly_volume: parseFloat(volume),
      entry_time: new Date().toISOString(),
    });
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 backdrop-blur-sm">
      <div className="bg-gray-800 p-6 rounded-xl w-96 border border-gray-600 shadow-2xl">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <span className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>
          Receive Product at {station.code}
        </h3>

        <div className="mb-6 bg-gray-700 p-4 rounded-lg border border-gray-600">
          <p className="text-sm text-gray-400 mb-1">Incoming Product</p>
          {activeBatch ? (
            <div>
              <p className="text-lg font-bold text-white">{activeBatch.product_name}</p>
              <p className="text-xs text-gray-300">{activeBatch.batch_name}</p>
              <div className="mt-2 text-xs bg-green-900 text-green-200 px-2 py-1 rounded inline-block">
                ✓ Ready to Receive
              </div>
            </div>
          ) : (
            <div className="text-yellow-400 text-sm flex items-center gap-2">
              <span>⚠️ No product detected at this station.</span>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Volume to Receive (m³)</label>
            <input
              type="number"
              value={volume}
              onChange={(e) => setVolume(e.target.value)}
              className="w-full bg-gray-900 text-white rounded px-3 py-2 border border-gray-600 focus:border-green-500 focus:outline-none"
              placeholder="Enter volume..."
              required
              min="1"
              disabled={!activeBatch}
            />
          </div>

          <div className="flex justify-end gap-2 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-300 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!activeBatch || mutation.isPending}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-500 disabled:opacity-50 disabled:cursor-not-allowed font-bold"
            >
              {mutation.isPending ? "Receiving..." : "Confirm Receipt"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
