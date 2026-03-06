import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import PipelineVisualization from "./PipelineVisualization";
import CreateBatchForm from "./CreateBatchForm";
import FlowEntryForm from "./FlowEntryForm";
import ShelvedBatchesList from "./ShelvedBatchesList";
import HistoryPane from "./HistoryPane";
import ReceivingOperations from "./ReceivingOperations";

export default function Dashboard() {
  const { data: viz } = useQuery({
    queryKey: ["visualization"],
    queryFn: () => axios.get("/api/visualization/current").then((r) => r.data),
    refetchInterval: 10000,
  });

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <header className="mb-8">
        <h1 className="text-4xl font-bold">Kenya Pipeline BatchTracking System</h1>
        <p className="text-gray-400">LINE 5</p>
      </header>

      <div className="space-y-8">
        {/* Upper Section: Visualization */}
        <div className="w-full space-y-8">
          <PipelineVisualization />
          
        </div>

        {/* Lower Section: Forms & Data */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Column 1: Operations (Forms) */}
          <div className="space-y-6">
            <CreateBatchForm />
            <FlowEntryForm />
            <ReceivingOperations />
            
          </div>

          {/* Column 2: History */}
          <div className="space-y-6">
            {viz?.stations && <HistoryPane stations={viz.stations} />}
          </div>

          {/* Column 3: Shelved Batches */}
          <div className="space-y-6">
            <ShelvedBatchesList />
          </div>
        </div>
      </div>

      {viz && (
        <div className="mt-8 text-center text-gray-400">
          Last updated: {new Date(viz.timestamp).toLocaleTimeString()}
        </div>
      )}
    </div>
  );
}
