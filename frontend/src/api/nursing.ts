export interface Elder {
  id: number;
  name: string;
  gender: string;
  phone?: string;
  family_contact?: string;
  health_summary?: string;
}

export interface ElderCreatePayload {
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

export interface RoomCreatePayload {
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

export interface BedCreatePayload {
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

export interface NursingProjectCreatePayload {
  name: string;
  category: string;
  description?: string;
  price: number;
}

export interface AlertRecord {
  id: number;
  device_name: string;
  severity: string;
  content: string;
  handled: boolean;
}

export interface AlertCreatePayload {
  elder_id?: number;
  device_name: string;
  severity: string;
  content: string;
}

export interface CheckInApplication {
  id: number;
  elder_id: number;
  preferred_room_type?: string;
  care_needs?: string;
  status: string;
}

export interface CheckInCreatePayload {
  elder_id: number;
  preferred_room_type?: string;
  care_needs?: string;
  status: string;
}

export async function listElders(): Promise<Elder[]> {
  return fetchJson('/api/nursing/elders');
}

export async function createElder(payload: ElderCreatePayload): Promise<Elder> {
  return postJson('/api/nursing/elders', payload);
}

export async function listRooms(): Promise<Room[]> {
  return fetchJson('/api/nursing/rooms');
}

export async function createRoom(payload: RoomCreatePayload): Promise<Room> {
  return postJson('/api/nursing/rooms', payload);
}

export async function listBeds(): Promise<Bed[]> {
  return fetchJson('/api/nursing/beds');
}

export async function createBed(payload: BedCreatePayload): Promise<Bed> {
  return postJson('/api/nursing/beds', payload);
}

export async function listNursingProjects(): Promise<NursingProject[]> {
  return fetchJson('/api/nursing/projects');
}

export async function createNursingProject(payload: NursingProjectCreatePayload): Promise<NursingProject> {
  return postJson('/api/nursing/projects', payload);
}

export async function listAlerts(): Promise<AlertRecord[]> {
  return fetchJson('/api/nursing/alerts');
}

export async function createAlert(payload: AlertCreatePayload): Promise<AlertRecord> {
  return postJson('/api/nursing/alerts', payload);
}

export async function listCheckIns(): Promise<CheckInApplication[]> {
  return fetchJson('/api/nursing/checkins');
}

export async function createCheckIn(payload: CheckInCreatePayload): Promise<CheckInApplication> {
  return postJson('/api/nursing/checkins', payload);
}

export async function seedDemoData(): Promise<{
  elders: number;
  rooms: number;
  beds: number;
  projects: number;
  alerts: number;
}> {
  const response = await fetch('/api/nursing/demo/seed', { method: 'POST' });
  if (!response.ok) {
    throw new Error('初始化演示数据失败');
  }
  return response.json();
}

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error('业务数据加载失败');
  }
  return response.json();
}

async function postJson<T>(url: string, payload: unknown): Promise<T> {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error('业务数据保存失败');
  }
  return response.json();
}
