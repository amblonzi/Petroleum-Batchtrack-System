export interface Product {
  id: number;
  name: string;
  code: string;
  color: string;
}

export interface Station {
  id: number;
  name: string;
  code: string;
  kilometer_post: number;
}

export interface Batch {
  id: number;
  name: string;
  product_id: number;
  source_station_id: number;
  total_volume: number;
  started_pumping_at?: string;
  finished_pumping_at?: string;
  status: "CREATED" | "PUMPING" | "COMPLETED";
  pumped_volume: number;
  created_by: number;
  created_at: string;
  product?: Product;
}

export interface FlowEntry {
  id: number;
  batch_id: number;
  station_id: number;
  entry_time: string;
  hourly_volume: number;
  entered_by: number;
  entered_at: string;
}
