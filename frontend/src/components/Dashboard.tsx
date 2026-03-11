import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "../services/api";
import { usePipeline } from "../context/PipelineContext";
import PipelineVisualization from "./PipelineVisualization";
import CreateBatchForm from "./CreateBatchForm";
import FlowEntryForm from "./FlowEntryForm";
import ShelvedBatchesList from "./ShelvedBatchesList";
import HistoryPane from "./HistoryPane";
import ReceivingOperations from "./ReceivingOperations";
import AdminPanel from "./AdminPanel";
import BatchLog from "./BatchLog";
import GainLoss from "./GainLoss";
import LiveBatchesPane from "./LiveBatchesPane";
import { useQueryClient } from "@tanstack/react-query";
import type { User } from "../types";
import { useEffect } from "react";
import { useAuthStore } from "../store/auth";

export default function Dashboard() {
  const [mainTab, setMainTab] = useState<"runsheet" | "admin" | "batchlog" | "gainloss">("runsheet");
  const [activeTab, setActiveTab] = useState<"operations" | "history" | "shelved">("operations");
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const kenyanTime = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Africa/Nairobi",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).format(currentTime);

  const kenyanDate = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Africa/Nairobi",
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(currentTime);

  const { pipelines, selectedPipeline, setSelectedPipeline, isLoading: pipelineLoading } = usePipeline();

  const { data: viz } = useQuery({
    queryKey: ["visualization", selectedPipeline?.line_number],
    queryFn: () => api.get(`/visualization/current?line=${selectedPipeline?.line_number}`).then((r) => r.data),
    refetchInterval: 10000,
    enabled: !!selectedPipeline
  });

  const queryClient = useQueryClient();
  const currentUser = queryClient.getQueryData<User>(["currentUser"]);
  const setToken = useAuthStore((s) => s.setToken);

  const handleLogout = () => {
    setToken(null);
    queryClient.clear();
  };

  return (
    <div className="h-screen w-full bg-gray-900 text-white flex flex-col overflow-hidden">
      {/* Top Navigation Bar */}
      <header className="bg-gray-800 border-b border-gray-700 flex items-center justify-between px-6 py-4 shrink-0 shadow-md z-10">
        <div className="flex items-center gap-8">
          <div className="flex flex-col">
            <h1 className="text-2xl font-bold tracking-tight text-blue-400">BATCHTRACK<span className="text-white">OS</span></h1>
            {pipelineLoading ? (
              <p className="text-xs text-gray-500 uppercase tracking-widest font-semibold mt-0.5">Loading Pipelines...</p>
            ) : (
              <div className="flex gap-1 mt-1">
                {pipelines.map(p => (
                  <button
                    key={p.id}
                    onClick={() => setSelectedPipeline(p)}
                    className={`text-xs px-2 py-0.5 rounded flex items-center gap-1 font-bold tracking-wider transition-colors border
                       ${selectedPipeline?.id === p.id
                        ? 'bg-blue-600/20 text-blue-300 border-blue-500/50'
                        : 'bg-gray-800 text-gray-400 border-gray-700 hover:bg-gray-700 hover:text-gray-200'}`}
                  >
                    <div className={`w-1.5 h-1.5 rounded-full ${selectedPipeline?.id === p.id ? 'bg-blue-400' : 'bg-gray-500'}`} />
                    {p.line_number}
                  </button>
                ))}
              </div>
            )}
          </div>

          <nav className="flex items-center gap-1 bg-gray-900/50 p-1 rounded-lg border border-gray-700">
            <button
              onClick={() => setMainTab("runsheet")}
              className={`px-6 py-2 rounded-md font-bold text-sm transition-all ${mainTab === "runsheet" ? "bg-blue-600 text-white shadow-lg" : "text-gray-400 hover:text-white hover:bg-gray-800"
                }`}
            >
              Runsheet
            </button>
            {currentUser?.is_admin && (
              <button
                onClick={() => setMainTab("admin")}
                className={`px-6 py-2 rounded-md font-bold text-sm transition-all ${mainTab === "admin" ? "bg-blue-600 text-white shadow-lg" : "text-gray-400 hover:text-white hover:bg-gray-800"
                  }`}
              >
                Admin
              </button>
            )}
            <button
              onClick={() => setMainTab("batchlog")}
              className={`px-6 py-2 rounded-md font-bold text-sm transition-all ${mainTab === "batchlog" ? "bg-blue-600 text-white shadow-lg" : "text-gray-400 hover:text-white hover:bg-gray-800"
                }`}
            >
              Batch Log
            </button>
            <button
              onClick={() => setMainTab("gainloss")}
              className={`px-6 py-2 rounded-md font-bold text-sm transition-all ${mainTab === "gainloss" ? "bg-blue-600 text-white shadow-lg" : "text-gray-400 hover:text-white hover:bg-gray-800"
                }`}
            >
              Gain/Loss
            </button>
          </nav>
        </div>

        <div className="flex items-center gap-6">
          <div className="flex flex-col items-end border-r border-gray-700 pr-6">
            <div className="text-[10px] font-black text-gray-500 uppercase tracking-[0.2em] mb-0.5">{kenyanDate}</div>
            <div className="text-2xl font-black text-white font-mono tracking-tighter tabular-nums leading-none">
              {kenyanTime}
            </div>
          </div>
          <div className="flex flex-col items-end">
            {viz && (
              <div className="text-[10px] text-green-400 font-black flex items-center gap-1.5 uppercase tracking-widest">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.6)]"></span>
                Live Sync: {new Date(viz.timestamp).toLocaleTimeString([], { hour12: false })}
              </div>
            )}
            <div className="text-[10px] text-gray-500 font-bold mt-1 uppercase tracking-tight">System Status: <span className="text-green-500/80">Optimal</span></div>
          </div>

          <button
            onClick={handleLogout}
            className="ml-2 p-2 rounded-lg bg-gray-700/50 hover:bg-red-600/20 text-gray-400 hover:text-red-400 transition-all border border-gray-600 hover:border-red-500/30 group"
            title="Log Out"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="w-5 h-5 group-hover:scale-110 transition-transform"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
          </button>
        </div>
      </header>

      {/* Main Responsive Content Area */}
      <main className="flex-1 overflow-hidden relative flex flex-col bg-gray-950/50">
        {mainTab === "runsheet" && (
          <div className="absolute inset-0 flex flex-col overflow-y-auto p-6 space-y-6 custom-scrollbar">
            {/* Visualizer stays at the top of runsheet */}
            <div className="w-full shrink-0">
              <PipelineVisualization />
            </div>

            {/* Lower Section: Tabs & Content */}
            <div className="bg-gray-800 rounded-xl shadow-lg border border-gray-700 flex flex-col min-h-0 flex-1 w-full">
              {/* Tab Navigation */}
              <div className="flex border-b border-gray-700">
                <button
                  onClick={() => setActiveTab("operations")}
                  className={`flex-1 py-4 px-6 text-center font-bold text-lg transition-colors ${activeTab === "operations"
                    ? "bg-blue-600 text-white"
                    : "text-gray-400 hover:text-white hover:bg-gray-750"
                    }`}
                >
                  Operations
                </button>
                <button
                  onClick={() => setActiveTab("history")}
                  className={`flex-1 py-4 px-6 text-center font-bold text-lg transition-colors border-l border-gray-700 ${activeTab === "history"
                    ? "bg-purple-600 text-white"
                    : "text-gray-400 hover:text-white hover:bg-gray-750"
                    }`}
                >
                  History
                </button>
                <button
                  onClick={() => setActiveTab("shelved")}
                  className={`flex-1 py-4 px-6 text-center font-bold text-lg transition-colors border-l border-gray-700 ${activeTab === "shelved"
                    ? "bg-yellow-600 text-white"
                    : "text-gray-400 hover:text-white hover:bg-gray-750"
                    }`}
                >
                  Shelved Batches
                </button>
              </div>

              {/* Tab Content */}
              <div className="p-6">
                {activeTab === "operations" && (
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <div className="space-y-6 lg:col-span-1">
                      <CreateBatchForm />
                      <FlowEntryForm />
                    </div>
                    <div className="lg:col-span-1">
                      <ReceivingOperations />
                    </div>
                    <div className="lg:col-span-1 h-full">
                      <LiveBatchesPane />
                    </div>
                  </div>
                )}

                {activeTab === "history" && (
                  <div className="max-w-4xl mx-auto">
                    {viz?.stations ? (
                      <HistoryPane stations={viz.stations} />
                    ) : (
                      <div className="text-center text-gray-400 py-10">Loading history...</div>
                    )}
                  </div>
                )}

                {activeTab === "shelved" && (
                  <div className="max-w-4xl mx-auto">
                    <ShelvedBatchesList />
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Placeholder Tabs */}
        {mainTab === "admin" && currentUser?.is_admin && (
          <AdminPanel />
        )}

        {mainTab === "batchlog" && (
          <BatchLog />
        )}

        {mainTab === "gainloss" && (
          <GainLoss />
        )}
      </main>
    </div>
  );
}
