export async function checkAgentHealth(): Promise<{ status: string }> {
  const response = await fetch('/api/agent/health');
  if (!response.ok) {
    throw new Error('Agent 服务不可用');
  }
  return response.json();
}

export async function sendAgentMessage(message: string): Promise<{ answer: string }> {
  const response = await fetch('/api/agent/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });

  if (!response.ok) {
    throw new Error('发送消息失败');
  }

  return response.json();
}

export async function requestCheckInRecommendation(
  elderName: string
): Promise<{ elder_name: string; suggestion: string }> {
  const response = await fetch('/api/agent/checkin/recommendation', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ elder_name: elderName })
  });

  if (!response.ok) {
    throw new Error('生成入住建议失败');
  }

  return response.json();
}

export async function requestCarePlan(
  elderName: string,
  careGoal: string
): Promise<{ elder_name: string; care_goal: string; plan: string }> {
  const response = await fetch('/api/agent/care-plan', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ elder_name: elderName, care_goal: careGoal })
  });

  if (!response.ok) {
    throw new Error('生成护理计划失败');
  }

  return response.json();
}

export async function requestAlertAnalysis(alertId: number): Promise<{ alert_id: number; analysis: string }> {
  const response = await fetch('/api/agent/alert-analysis', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ alert_id: alertId })
  });

  if (!response.ok) {
    throw new Error('生成告警分析失败');
  }

  return response.json();
}

export interface AlertStatItem {
  severity: string;
  count: number;
}

export interface RecentAlertItem {
  device_name: string;
  severity: string;
  content: string;
  created_at: string | null;
  handled: boolean;
}

export interface TopDeviceItem {
  device_name: string;
  count: number;
}

export interface HealthProfile {
  elder_id: number;
  elder_name: string;
  health_summary: string;
  alert_total: number;
  alert_stats: AlertStatItem[];
  recent_alerts: RecentAlertItem[];
  top_devices: TopDeviceItem[];
  risk_score: number;
  risk_level: string;
  recommended_projects: string[];
  summary: string;
}

export async function requestHealthProfile(elderId: number): Promise<HealthProfile> {
  const response = await fetch('/api/agent/health-profile', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ elder_id: elderId })
  });

  if (!response.ok) {
    throw new Error('生成健康画像失败');
  }

  return response.json();
}

export interface AdmissionPreview {
  run_id: number;
  status: string;
  elder_name: string;
  bed_id: number;
  bed_no: string;
  preview_summary: string;
  reservation_token: string;
  expires_at: string;
}

export interface AdmissionResult {
  run_id: number;
  status: string;
  elder_id: number;
  bed_id?: number;
  message: string;
}

async function parseAdmissionError(response: Response, fallback: string): Promise<never> {
  const err = await response.json().catch(() => null);
  throw new Error(err?.detail?.message || fallback);
}

export async function requestAdmissionPreview(elderId: number): Promise<AdmissionPreview> {
  const response = await fetch('/api/agent/admission/preview', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ elder_id: elderId })
  });
  if (!response.ok) {
    await parseAdmissionError(response, '生成入住预览失败');
  }
  return response.json();
}

export async function requestAdmissionConfirm(
  runId: number,
  token: string
): Promise<AdmissionResult> {
  const response = await fetch('/api/agent/admission/confirm', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ run_id: runId, reservation_token: token })
  });
  if (!response.ok) {
    await parseAdmissionError(response, '确认入住失败');
  }
  return response.json();
}

export async function requestAdmissionCancel(
  runId: number,
  token: string
): Promise<AdmissionResult> {
  const response = await fetch('/api/agent/admission/cancel', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ run_id: runId, reservation_token: token })
  });
  if (!response.ok) {
    await parseAdmissionError(response, '取消入住失败');
  }
  return response.json();
}
