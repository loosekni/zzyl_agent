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
