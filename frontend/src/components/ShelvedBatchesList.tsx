import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import type { Batch } from "../types";
import EditBatchModal from "./EditBatchModal";

export default function ShelvedBatchesList() {
  const [editingBatch, setEditingBatch] = useState<Batch | null>(null);
  const { data: batches, isLoading } = useQuery({
    queryKey: ["batches"],
    queryFn: () => axios.get<Batch[]>("/batches/").then((r) => r.data),
    refetchInterval: 5000,
  });

  const shelvedBatches = batches?.filter((b) => b.status === "CREATED") || [];

  if (isLoading) return <div className="text-gray-400">Loading batches...</div>;

  return (
    <div className="bg-gray-800 p-6 rounded-xl">
      <h3 className="text-xl font-bold mb-4 text-white">Shelved Batches (Ready to Pump)</h3>
      {shelvedBatches.length === 0 ? (
        <p className="text-gray-400">No shelved batches found.</p>
      ) : (
        <div className="space-y-4">
          {shelvedBatches.map((batch) => (
            <div
              key={batch.id}
              className="bg-gray-700 p-4 rounded-lg border-l-4 border-yellow-500 flex justify-between items-center group"
            >
              <div>
                <h4 className="font-bold text-white">{batch.name}</h4>
                <p className="text-sm text-gray-300">
                  Volume: {batch.total_volume.toLocaleString()} m³
                </p>
                <p className="text-xs text-gray-400">
                  Created: {new Date(batch.created_at).toLocaleString()}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <span className="px-2 py-1 bg-yellow-900 text-yellow-200 text-xs rounded-full">
                  {batch.status}
                </span>
                <button
                  onClick={() => setEditingBatch(batch)}
                  className="text-gray-400 hover:text-white opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                  </svg>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {editingBatch && (
        <EditBatchModal
          batch={editingBatch}
          onClose={() => setEditingBatch(null)}
        />
      )}
    </div>
  );
}
