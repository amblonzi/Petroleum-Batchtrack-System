import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "../services/api";
import type { Batch, Station } from "../types";
import { usePipeline } from "../context/PipelineContext";
import StatusModal from "./StatusModal";

interface FlowEntryData {
  batch_id: number;
  station_id: number;
  entry_time: string;
  hourly_volume: number;
}

export default function FlowEntryForm() {
  const [selectedBatch, setSelectedBatch] = useState("");
  const [volume, setVolume] = useState("");
  const [stationId, setStationId] = useState("");
  const { selectedPipeline } = usePipeline();
  const queryClient = useQueryClient();

  const [modal, setModal] = useState<{ isOpen: boolean; type: 'success' | 'error'; title: string; message: string }>({
    isOpen: false,
    type: 'success',
    title: '',
    message: ''
  });

  const { data: batches } = useQuery<Batch[]>({
    queryKey: ["batches", selectedPipeline?.line_number],
    queryFn: () => api.get(`/batches/?line=${selectedPipeline?.line_number}`).then((r) => r.data),
    enabled: !!selectedPipeline,
  });

  const { data: stations } = useQuery<Station[]>({
    queryKey: ["stations", selectedPipeline?.line_number],
    queryFn: () => api.get(`/stations/?line=${selectedPipeline?.line_number}`).then((res) => res.data),
    enabled: !!selectedPipeline,
  });

  // Filter batches to only allow:
  // 1. Shelved batches (CREATED)
  // 2. The LATEST pumping batch (PUMPING)
  const pumpingBatches = batches?.filter((b) => b.status === "PUMPING") || [];
  const latestPumpingBatch = pumpingBatches.sort((a, b) => {
    const dateA = new Date(a.started_pumping_at || 0).getTime();
    const dateB = new Date(b.started_pumping_at || 0).getTime();
    return dateB - dateA;
  })[0];

  const selectableBatches = batches?.filter(
    (b) =>
      b.status === "CREATED" ||
      (b.status === "PUMPING" && b.id === latestPumpingBatch?.id)
  );

  const mutation = useMutation({
    mutationFn: (newFlow: FlowEntryData) => {
      return api.post("/flow-entries/", newFlow);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["visualization"] });
      queryClient.invalidateQueries({ queryKey: ["batches"] });
      setVolume("");
      setStationId("");
      setModal({
        isOpen: true,
        type: 'success',
        title: 'FLOW RECORDED',
        message: 'The hourly flow rate has been successfully logged to the database.'
      });
    },
    onError: (error) => {
      setModal({
        isOpen: true,
        type: 'error',
        title: 'RECORDING ERROR',
        message: 'Could not record flow data: ' + error
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBatch || !volume || !stationId) return;

    mutation.mutate({
      batch_id: parseInt(selectedBatch),
      station_id: parseInt(stationId),
      hourly_volume: parseFloat(volume),
      entry_time: new Date().toISOString(),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="bg-gray-800 p-6 rounded-lg shadow-lg relative">
      <StatusModal
        isOpen={modal.isOpen}
        onClose={() => setModal(prev => ({ ...prev, isOpen: false }))}
        type={modal.type}
        title={modal.title}
        message={modal.message}
      />
      <h3 className="text-xl font-bold text-white mb-4">Record Hourly Flow</h3>
      <div className="space-y-4">
        <div>
          <label className="block text-gray-400 mb-1">Station</label>
          <select
            value={stationId}
            onChange={(e) => setStationId(e.target.value)}
            className="w-full bg-gray-700 text-white p-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
            required
            disabled={!selectedPipeline}
          >
            <option value="">Select Station</option>
            {stations?.filter(s => ["lifting", "receiving"].includes(s.station_type)).map((s) => (
              <option key={s.id} value={s.id}>
                {s.code} - {s.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-gray-400 mb-1">Batch</label>
          <select
            value={selectedBatch}
            onChange={(e) => setSelectedBatch(e.target.value)}
            className="w-full bg-gray-700 text-white p-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
            required
          >
            <option value="">Select Batch to Pump</option>
            {selectableBatches?.map((batch) => (
              <option key={batch.id} value={batch.id}>
                {batch.name} ({batch.status})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-gray-400 mb-1">Volume (m³)</label>
          <input
            type="number"
            value={volume}
            onChange={(e) => setVolume(e.target.value)}
            className="w-full bg-gray-700 text-white p-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
            placeholder="Enter volume"
            required
          />
        </div>

        <button
          type="submit"
          disabled={mutation.isPending}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors disabled:opacity-50"
        >
          {mutation.isPending ? "Recording..." : "Record Flow"}
        </button>
      </div>
    </form>
  );
}
