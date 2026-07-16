import { Button, Card, Input, Space, Typography, message as antdMessage } from 'antd';
import { useEffect, useState } from 'react';

import {
  checkAgentHealth,
  requestAlertAnalysis,
  requestCarePlan,
  requestCheckInRecommendation,
  sendAgentMessage
} from '../api/agent';

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
  const [carePlanElderName, setCarePlanElderName] = useState('');
  const [careGoal, setCareGoal] = useState('');
  const [carePlan, setCarePlan] = useState('');
  const [alertId, setAlertId] = useState('');
  const [alertAnalysis, setAlertAnalysis] = useState('');
  const [loading, setLoading] = useState(false);
  const [recommendLoading, setRecommendLoading] = useState(false);
  const [carePlanLoading, setCarePlanLoading] = useState(false);
  const [alertLoading, setAlertLoading] = useState(false);

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

  const handleCarePlan = async () => {
    setCarePlanLoading(true);
    try {
      const data = await requestCarePlan(carePlanElderName, careGoal);
      setCarePlan(data.plan);
    } catch (error) {
      antdMessage.error(error instanceof Error ? error.message : '请求失败');
    } finally {
      setCarePlanLoading(false);
    }
  };

  const handleAlertAnalysis = async () => {
    setAlertLoading(true);
    try {
      const data = await requestAlertAnalysis(Number(alertId));
      setAlertAnalysis(data.analysis);
    } catch (error) {
      antdMessage.error(error instanceof Error ? error.message : '请求失败');
    } finally {
      setAlertLoading(false);
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

      <Card title="护理计划生成">
        <Space direction="vertical" style={{ width: '100%' }}>
          <Input
            value={carePlanElderName}
            placeholder="输入老人姓名"
            onChange={(event) => setCarePlanElderName(event.target.value)}
          />
          <Input.TextArea
            value={careGoal}
            rows={3}
            placeholder="输入护理目标，例如：控制跌倒风险、改善睡眠、加强慢病照护"
            onChange={(event) => setCareGoal(event.target.value)}
          />
          <Button type="primary" loading={carePlanLoading} onClick={handleCarePlan}>
            生成护理计划
          </Button>
          {carePlan ? <Card type="inner">{carePlan}</Card> : null}
        </Space>
      </Card>

      <Card title="告警分析">
        <Space direction="vertical" style={{ width: '100%' }}>
          <Input
            value={alertId}
            placeholder="输入告警 ID"
            onChange={(event) => setAlertId(event.target.value)}
          />
          <Button type="primary" loading={alertLoading} onClick={handleAlertAnalysis}>
            生成告警分析
          </Button>
          {alertAnalysis ? <Card type="inner">{alertAnalysis}</Card> : null}
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
