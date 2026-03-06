import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import type { Product } from "../types";

export default function CreateBatchForm() {
  const [name, setName] = useState("");
  const [productId, setProductId] = useState("");
  const [volume, setVolume] = useState("");
  const queryClient = useQueryClient();

  const { data: products } = useQuery<Product[]>({
    queryKey: ["products"],
    queryFn: () => axios.get("/api/products/").then((r) => r.data),
  });

  const mutation = useMutation({
    mutationFn: (data: any) => axios.post("/api/batches/", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["batches"] }); // Invalidate batches list
      setName("");
      setProductId("");
      setVolume("");
    },
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
    </div>
  );
}
