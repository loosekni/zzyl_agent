import { Button, Card, Input, Space, Typography, message as antdMessage } from 'antd';
import { useEffect, useState } from 'react';

import { checkAgentHealth, requestCheckInRecommendation, sendAgentMessage } from '../api/agent';

const { Title, Paragraph, Text } = Typography;

interface AgentHomePageProps {
  embedded?: boolean;
}

export function AgentHomePage({ embedded = false }: AgentHomePageProps) {
  const [health, setHealth] = useState('检查中');
  const [input, setInput] = useState('帮我为一位需要护理的老人生成入住建议');
  const [answer, setAnswer] = useState('');
  const [elderName, setElderName] = useState('');
  const [recommendation, setRecommendation] = useState('');
  const [loading, setLoading] = useState(false);
  const [recommendLoading, setRecommendLoading] = useState(false);

  useEffect(() => {
    checkAgentHealth()
      .then((data) => setHealth(data.status))
      .catch(() => setHealth('offline'));
  }, []);

  const handleSend = async () => {
    setLoading(true);
    try {
      const data = await sendAgentMessage(input);
      setAnswer(data.answer);
    } catch (error) {
      antdMessage.error(error instanceof Error ? error.message : '请求失败');
    } finally {
      setLoading(false);
    }
  };

  const handleRecommend = async () => {
    setRecommendLoading(true);
    try {
      const data = await requestCheckInRecommendation(elderName);
      setRecommendation(data.suggestion);
    } catch (error) {
      antdMessage.error(error instanceof Error ? error.message : '请求失败');
    } finally {
      setRecommendLoading(false);
    }
  };

  const content = (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Card>
        <Title level={3}>单体 Agent 平台</Title>
        <Paragraph>
          当前先提供 FastAPI + LangGraph 的最小对话入口，后续逐步迁移入住、护理、告警和健康评估流程。
        </Paragraph>
        <Text type={health === 'ok' ? 'success' : 'secondary'}>后端状态：{health}</Text>
      </Card>

      <Card title="入住推荐">
        <Space direction="vertical" style={{ width: '100%' }}>
          <Input
            value={elderName}
            placeholder="输入老人姓名"
            onChange={(event) => setElderName(event.target.value)}
          />
          <Button type="primary" loading={recommendLoading} onClick={handleRecommend}>
            生成入住建议
          </Button>
          {recommendation ? <Card type="inner">{recommendation}</Card> : null}
        </Space>
      </Card>

      <Card title="Agent 对话">
        <Space direction="vertical" style={{ width: '100%' }}>
          <Input.TextArea value={input} rows={4} onChange={(event) => setInput(event.target.value)} />
          <Button type="primary" loading={loading} onClick={handleSend}>
            发送
          </Button>
          {answer ? <Card type="inner">{answer}</Card> : null}
        </Space>
      </Card>
    </Space>
  );

  if (embedded) {
    return content;
  }

  return <div style={{ minHeight: '100vh', padding: 32, background: '#f5f7fb' }}>{content}</div>;
}
