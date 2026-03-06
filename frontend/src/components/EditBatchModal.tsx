import { useState } from "react";
import axios from "axios";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { Batch } from "../types";

interface EditBatchModalProps {
  batch: Batch;
  onClose: () => void;
}

export default function EditBatchModal({ batch, onClose }: EditBatchModalProps) {
  const [name, setName] = useState(batch.name);
  const [totalVolume, setTotalVolume] = useState(batch.total_volume);
  const queryClient = useQueryClient();

  const updateMutation = useMutation({
    mutationFn: async (data: { name: string; total_volume: number }) => {
      await axios.put(`/api/batches/${batch.id}`, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["batches"] });
      onClose();
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate({ name, total_volume: totalVolume });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-gray-800 p-6 rounded-xl w-96 border border-gray-700">
        <h3 className="text-xl font-bold text-white mb-4">Edit Batch</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Batch Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-gray-700 text-white rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Total Volume (m³)</label>
            <input
              type="number"
              value={totalVolume}
              onChange={(e) => setTotalVolume(Number(e.target.value))}
              className="w-full bg-gray-700 text-white rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              required
              min="1"
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
              disabled={updateMutation.isPending}
              className="px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-500 disabled:opacity-50"
            >
              {updateMutation.isPending ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
