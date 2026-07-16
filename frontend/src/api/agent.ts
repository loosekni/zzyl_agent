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
