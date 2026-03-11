import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "../services/api";
import type { Product } from "../types";
import { usePipeline } from "../context/PipelineContext";
import StatusModal from "./StatusModal";

export default function CreateBatchForm() {
  const [name, setName] = useState("");
  const [productId, setProductId] = useState("");
  const [volume, setVolume] = useState("");
  const { selectedPipeline } = usePipeline();
  const queryClient = useQueryClient();
  const [showStatus, setShowStatus] = useState(false);
  const [statusType, setStatusType] = useState<'success' | 'error'>('success');
  const [statusInfo, setStatusInfo] = useState({ title: "", message: "" });

  const { data: products } = useQuery<Product[]>({
    queryKey: ["products"],
    queryFn: () => api.get("/products/").then((r) => r.data),
  });

  const mutation = useMutation({
    mutationFn: (data: any) => api.post(`/batches/?line=${selectedPipeline?.line_number}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["batches"] }); // Invalidate batches list
      setName("");
      setProductId("");
      setVolume("");
      setStatusType('success');
      setStatusInfo({
        title: "BATCH CREATED",
        message: `Batch "${name}" has been successfully created for Line ${selectedPipeline?.line_number}`
      });
      setShowStatus(true);
    },
    onError: (error: any) => {
      setStatusType('error');
      setStatusInfo({
        title: "CREATION FAILED",
        message: error.response?.data?.detail || "An error occurred while creating the batch."
      });
      setShowStatus(true);
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate({
      name,
      product_id: Number(productId),
      total_volume: Number(volume),
      // started_pumping_at is no longer sent here, handled by backend default or flow entry
    });
  };

  return (
    <div className="bg-gray-800 p-6 rounded-xl">
      <h3 className="text-xl font-bold mb-4 text-white">Create New Batch</h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          placeholder="Batch Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:border-green-500 focus:outline-none"
          required
        />
        <input
          type="number"
          placeholder="Volume (m³)"
          value={volume}
          onChange={(e) => setVolume(e.target.value)}
          className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:border-green-500 focus:outline-none"
          required
        />
        <select
          value={productId}
          onChange={(e) => setProductId(e.target.value)}
          className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:border-green-500 focus:outline-none"
          required
        >
          <option value="">Select Product</option>
          {products?.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
        <button
          type="submit"
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded font-bold transition-colors"
        >
          Create Batch (Shelved)
        </button>
      </form>

      <StatusModal
        isOpen={showStatus}
        onClose={() => setShowStatus(false)}
        type={statusType}
        title={statusInfo.title}
        message={statusInfo.message}
      />
    </div>
  );
}
