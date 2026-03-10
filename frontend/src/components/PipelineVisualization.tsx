
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "../services/api";
import type { Station } from "../types";
import ReceiveProductModal from "./ReceiveProductModal";
import { usePipeline } from "../context/PipelineContext";

interface VisualizationData {
  timestamp: string;
  batches: Array<{
    batch_id: number;
    batch_name: string;
    product_name: string;
    color: string;
    leading_edge_km: number;
    trailing_edge_km: number;
    length_km: number;
    receiving: boolean;
  }>;
  total_pipeline_length: number;
  line_fill_rate: number;
  stations: (Station & { cumulative_volume: number; received_volume: number })[];
}

export default function PipelineVisualization() {
  const { selectedPipeline } = usePipeline();
  const [receivingStation, setReceivingStation] = useState<Station | null>(null);
  const [historyMode, setHistoryMode] = useState(false);
  const [historyDate, setHistoryDate] = useState(new Date().toISOString().slice(0, 16)); // YYYY-MM-DDTHH:mm

  const { data: viz } = useQuery<VisualizationData>({
    queryKey: ["visualization", selectedPipeline?.line_number, historyMode, historyDate],
    queryFn: async () => {
      if (!selectedPipeline) return null;
      const url = historyMode
        ? `/visualization/history?line=${selectedPipeline.line_number}&timestamp=${new Date(historyDate).toISOString()}`
        : `/visualization/current?line=${selectedPipeline.line_number}`;
      const res = await api.get(url);
      return res.data;
    },
    refetchInterval: historyMode ? false : 5000,
    enabled: !!selectedPipeline,
  });

  if (!viz || !selectedPipeline) return <div className="text-white">Loading pipeline...</div>;

  const PIPELINE_LENGTH = viz.total_pipeline_length;
  const VOLUME_PER_KM = viz.line_fill_rate;

  const getActiveBatch = (stationKm: number) => {
    return (
      viz.batches.find(
        (b) => b.leading_edge_km >= stationKm && b.trailing_edge_km <= stationKm
      ) || null
    );
  };

  return (
    <div className="bg-gray-900 p-6 rounded-xl">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-white">{selectedPipeline.name} Status</h2>
        <div className="flex items-center gap-4 bg-gray-800 p-2 rounded-lg border border-gray-700">
          <label className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
            <input
              type="checkbox"
              checked={historyMode}
              onChange={(e) => setHistoryMode(e.target.checked)}
              className="form-checkbox h-4 w-4 text-blue-600 rounded bg-gray-700 border-gray-600"
            />
            Historical View
          </label>

          {historyMode && (
            <input
              type="datetime-local"
              value={historyDate}
              onChange={(e) => setHistoryDate(e.target.value)}
              className="bg-gray-900 text-white text-sm rounded px-2 py-1 border border-gray-600 focus:border-blue-500 outline-none"
            />
          )}
        </div>
      </div>

      {/* Pipeline Container */}
      <div className="relative h-[250px] mt-12 select-none w-full">

        {/* The Thin Cylindrical Pipe Frame */}
        <div className="absolute top-1/2 left-0 right-0 h-10 -mt-5 bg-gradient-to-b from-gray-400 via-gray-200 to-gray-500 rounded-full border border-gray-600 shadow-xl overflow-hidden z-0">
          {/* Pipe Shine/Metallic effect */}
          <div className="absolute top-0 left-0 right-0 h-1/2 bg-white opacity-20 blur-[1px]"></div>
          <div className="absolute bottom-0 left-0 right-0 h-1/3 bg-black opacity-10 blur-[1px]"></div>

          {/* Batches inside the pipe */}
          {viz.batches?.map((batch) => (
            <div
              key={batch.batch_id}
              className={`absolute top-0.5 bottom-0.5 transition-all duration-1000 animate-flow ${batch.receiving ? "animate-pulse brightness-110" : ""
                }`}
              style={{
                left: `${(batch.trailing_edge_km / PIPELINE_LENGTH) * 100}%`,
                width: `${(batch.length_km / PIPELINE_LENGTH) * 100}%`,
                backgroundColor: batch.color,
                boxShadow: "inset 0 1px 2px rgba(255,255,255,0.3), inset 0 -1px 2px rgba(0,0,0,0.3)"
              }}
            >
              {/* Batch Text inside the thin pipe might be too small, so we might show it on hover or if it's long enough */}
              {/* For longer batches, show name clipped */}
              <div className="h-full flex items-center justify-center text-[10px] font-bold text-white/90 overflow-hidden whitespace-nowrap px-1">
                {batch.length_km > 10 && <span className="drop-shadow-sm truncate">{batch.batch_name}</span>}
              </div>
            </div>
          ))}
        </div>


        {/* Head and Tail Volume Tags */}
        {viz.batches?.map((batch) => (
          <div key={`batch-tags-${batch.batch_id}`}>

            {/* Tail Tag (Trailing Edge) - ABOVE pipe */}
            <div
              className="absolute top-1/2 -mt-5 z-20 pointer-events-none transition-all duration-1000"
              style={{
                left: `${(batch.trailing_edge_km / PIPELINE_LENGTH) * 100}%`,
              }}
            >
              {/* Line to interface */}
              <div className="absolute top-0 -left-px w-[1px] h-10 -mt-6 bg-white/40"></div>

              {/* Tag Bubbles: Volume (upper) + Distance (lower) */}
              <div className="absolute -top-14 -translate-x-1/2 flex flex-col items-center gap-0.5">
                {/* Upper: Volume */}
                <div className="bg-gray-800/90 backdrop-blur-sm text-white text-[9px] font-mono px-1 py-0.5 rounded border border-gray-600 shadow-lg whitespace-nowrap">
                  <span className="text-[8px] text-gray-400 mr-1">Vol:</span>
                  {Math.floor(batch.trailing_edge_km * VOLUME_PER_KM).toLocaleString()} m³
                </div>
                {/* Lower: Distance in km */}
                <div className="bg-gray-900/90 backdrop-blur-sm text-amber-400 text-[9px] font-mono px-1 py-0.5 rounded border border-amber-700/50 shadow-lg whitespace-nowrap">
                  <span className="text-[8px] text-amber-600 mr-1">Dist:</span>
                  {batch.trailing_edge_km.toFixed(2)} km
                </div>
              </div>
            </div>

            {/* Head Tag (Leading Edge) - BELOW pipe */}
            <div
              className="absolute top-1/2 mt-5 z-20 pointer-events-none transition-all duration-1000"
              style={{
                left: `${(batch.leading_edge_km / PIPELINE_LENGTH) * 100}%`,
              }}
            >
              {/* Line to interface */}
              <div className="absolute top-0 -left-px w-[1px] h-10 -mt-4 bg-white/40"></div>

              {/* Tag Bubbles: Volume (upper) + Distance (lower) */}
              <div className="absolute top-6 -translate-x-1/2 flex flex-col items-center gap-0.5">
                {/* Upper: Volume */}
                <div className="bg-gray-800/90 backdrop-blur-sm text-white text-[9px] font-mono px-1 py-0.5 rounded border border-gray-600 shadow-lg whitespace-nowrap">
                  <span className="text-[8px] text-gray-400 mr-1">Vol:</span>
                  {Math.floor(batch.leading_edge_km * VOLUME_PER_KM).toLocaleString()} m³
                </div>
                {/* Lower: Distance in km */}
                <div className="bg-gray-900/90 backdrop-blur-sm text-amber-400 text-[9px] font-mono px-1 py-0.5 rounded border border-amber-700/50 shadow-lg whitespace-nowrap">
                  <span className="text-[8px] text-amber-600 mr-1">Dist:</span>
                  {batch.leading_edge_km.toFixed(2)} km
                </div>
              </div>
            </div>

          </div>
        ))}



        {/* Stations and Calibrations */}
        {viz.stations?.map((dynamicStation) => {
          const isReceivingStation = dynamicStation.station_type === "receiving";
          const activeBatch = getActiveBatch(dynamicStation.kilometer_post);
          const cumulativeVol = dynamicStation.kilometer_post * VOLUME_PER_KM;

          return (
            <div
              key={dynamicStation.code}
              className="absolute top-0 bottom-0 w-0 flex flex-col items-center justify-center group z-10"
              style={{
                left: `${(dynamicStation.kilometer_post / PIPELINE_LENGTH) * 100}%`,
              }}
            >
              {/* Calibration Tick Line */}
              <div className="absolute top-1/2 -mt-8 h-16 w-[2px] bg-black/30 z-0"></div> {/* Shadow behind tick */}
              <div className="absolute top-1/2 -mt-8 h-16 w-[1px] bg-yellow-500 z-10"></div>

              {/* Top Label: Station Code */}
              <div className="absolute top-[15%] flex flex-col items-center">
                <div
                  className={`flex flex-col items-center p-1 rounded backdrop-blur-md border shadow-md transition-all ${isReceivingStation
                    ? "bg-blue-900/80 border-blue-500 text-blue-100"
                    : "bg-gray-800/80 border-gray-600 text-gray-300"
                    }`}
                >
                  <span className="text-xs font-bold whitespace-nowrap leading-none">
                    {dynamicStation.code === "PS8" && selectedPipeline.line_number === "L5" ? "PS8 - Konza" : dynamicStation.code}
                  </span>
                  <span className="text-[9px] opacity-75 leading-none mt-0.5">{dynamicStation.kilometer_post.toFixed(0)} km</span>
                </div>

                {/* Receive Button */}
                {isReceivingStation && dynamicStation && !historyMode && (
                  <button
                    onClick={() => setReceivingStation(dynamicStation)}
                    className={`mt-1 px-2 py-0.5 text-[9px] font-bold rounded uppercase tracking-wider transition-all shadow-lg border ${activeBatch
                      ? "bg-green-600 border-green-400 text-white hover:bg-green-500 hover:scale-105 animate-pulse"
                      : "bg-gray-700 border-gray-600 text-gray-400 hover:bg-gray-600"
                      }`}
                  >
                    Receive
                  </button>
                )}

                {/* Received Volume */}
                {dynamicStation && dynamicStation.received_volume > 0 && (
                  <span className="text-[9px] text-green-400 whitespace-nowrap bg-gray-900/90 px-1 py-0.5 rounded mt-1 border border-green-900 shadow-sm font-mono">
                    +{dynamicStation.received_volume.toLocaleString()}
                  </span>
                )}
              </div>

              {/* Bottom Label: Cumulative Volume */}
              <div className="absolute bottom-[25%] flex flex-col items-center">
                <span className="text-[10px] font-mono text-gray-400 whitespace-nowrap bg-gray-900/80 px-1.5 py-0.5 rounded border border-gray-700 hover:text-white hover:border-gray-500 transition-colors cursor-default">
                  {cumulativeVol.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </span>
              </div>
            </div>
          );
        })}

        {/* Continuous Line Profile Calibrations */}
        <div className="absolute bottom-4 left-0 right-0 h-[40px] pointer-events-none">
          {/* Main Axis Line */}
          <div className="absolute top-0 left-0 right-0 h-[1px] bg-gray-600"></div>

          {/* Calibration Marks every 50km + Pipeline End */}
          {Array.from({ length: Math.ceil(PIPELINE_LENGTH / 50) + 1 }, (_, i) => i * 50).map((km, i) => {
            if (km > PIPELINE_LENGTH && km - PIPELINE_LENGTH > 25) return null; // Avoid drawing a mark too close to the end
            const actualKm = km > PIPELINE_LENGTH ? PIPELINE_LENGTH : km;
            const volume = actualKm * VOLUME_PER_KM;
            const leftPercent = (actualKm / PIPELINE_LENGTH) * 100;

            return (
              <div
                key={i}
                className="absolute top-0 flex flex-col items-center"
                style={{ left: `${leftPercent}%` }}
              >
                <div className="h-2 w-[1px] bg-gray-400"></div>
                <div className="text-[9px] text-gray-400 font-mono mt-1 w-12 text-center -translate-x-1/2 ml-px">{Math.round(actualKm)} km</div>
                <div className="text-[8px] text-blue-400/80 font-mono mt-0.5 w-16 text-center -translate-x-1/2 ml-px">{Math.floor(volume).toLocaleString()} m³</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="mt-4 flex flex-wrap justify-center gap-6 text-xs text-gray-400">
        <div className="flex items-center gap-2">
          <div className="w-6 h-3 bg-gradient-to-b from-gray-400 via-gray-200 to-gray-500 rounded-full border border-gray-600"></div>
          <span>Pipeline ({selectedPipeline.total_length_km.toFixed(0)}km)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-0.5 h-4 bg-yellow-500"></div>
          <span>Station / Calibration</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_5px_rgba(59,130,246,0.8)]"></div>
          <span>Active Batch</span>
        </div>
      </div>

      {/* Receive Modal */}
      {receivingStation && (
        <ReceiveProductModal
          station={receivingStation}
          activeBatch={getActiveBatch(receivingStation.kilometer_post)}
          onClose={() => setReceivingStation(null)}
        />
      )}
    </div>
  );
}
