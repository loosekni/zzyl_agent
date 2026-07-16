export interface Elder {
  id: number;
  name: string;
  gender: string;
  phone?: string;
  family_contact?: string;
  health_summary?: string;
}

export interface Room {
  id: number;
  floor: string;
  room_no: string;
  room_type: string;
}

export interface Bed {
  id: number;
  room_id: number;
  bed_no: string;
  status: string;
}

export interface NursingProject {
  id: number;
  name: string;
  category: string;
  price: number;
}

export interface AlertRecord {
  id: number;
  device_name: string;
  severity: string;
  content: string;
  handled: boolean;
}

export async function listElders(): Promise<Elder[]> {
  return fetchJson('/api/nursing/elders');
}

export async function listRooms(): Promise<Room[]> {
  return fetchJson('/api/nursing/rooms');
}

export async function listBeds(): Promise<Bed[]> {
  return fetchJson('/api/nursing/beds');
}

export async function listNursingProjects(): Promise<NursingProject[]> {
  return fetchJson('/api/nursing/projects');
}

export async function listAlerts(): Promise<AlertRecord[]> {
  return fetchJson('/api/nursing/alerts');
}

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error('业务数据加载失败');
  }
  return response.json();
}
