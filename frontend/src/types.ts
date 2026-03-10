export interface Pipeline {
  id: number;
  line_number: string;
  name: string;
  description: string;
  total_length_km: number;
  line_fill_rate: number;
  is_active: boolean;
}

export interface User {
  id: number;
  username: string;
  full_name: string | null;
  is_active: boolean;
  is_admin: boolean;
}

export interface Product {
  id: number;
  name: string;
  code: string;
  color: string;
}

export interface Station {
  id: number;
  pipeline_id: number;
  name: string;
  code: string;
  kilometer_post: number;
  station_type: "lifting" | "intermediate" | "receiving";
}

export interface Batch {
  id: number;
  pipeline_id: number;
  name: string;
  product_id: number;
  source_station_id: number;
  total_volume: number;
  started_pumping_at?: string;
  finished_pumping_at?: string;
  status: "CREATED" | "PUMPING" | "COMPLETED";
  pumped_volume: number;
  received_volume: number;
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
