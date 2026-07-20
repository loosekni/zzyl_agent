import { RobotOutlined, TeamOutlined } from '@ant-design/icons';
import { Button, Card, Input, Select, Space, Typography, message as antdMessage } from 'antd';
import { useEffect, useRef, useState } from 'react';

import {
  checkAgentHealth,
  requestAlertAnalysis,
  requestCarePlan,
  requestCheckInRecommendation,
  streamAgentMessage
} from '../api/agent';
import { type Elder, listElders } from '../api/nursing';
import { AdmissionCard } from '../components/AdmissionCard';
import { HealthProfileCard } from '../components/HealthProfileCard';

const { Title, Paragraph, Text } = Typography;

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface AgentHomePageProps {
  embedded?: boolean;
}

export function AgentHomePage({ embedded = false }: AgentHomePageProps) {
  const [health, setHealth] = useState('检查中');
  const [elders, setElders] = useState<Elder[]>([]);

  // 对话（多轮）
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // 入住推荐
  const [recommendElderName, setRecommendElderName] = useState<string>();
  const [recommendation, setRecommendation] = useState('');
  const [recommendLoading, setRecommendLoading] = useState(false);

  // 护理计划
  const [carePlanElderName, setCarePlanElderName] = useState<string>();
  const [careGoal, setCareGoal] = useState('');
  const [carePlan, setCarePlan] = useState('');
  const [carePlanLoading, setCarePlanLoading] = useState(false);

  // 告警分析
  const [alertId, setAlertId] = useState('');
  const [alertAnalysis, setAlertAnalysis] = useState('');
  const [alertLoading, setAlertLoading] = useState(false);

  useEffect(() => {
    checkAgentHealth()
      .then((data) => setHealth(data.status))
      .catch(() => setHealth('offline'));
    listElders().then(setElders).catch(() => setElders([]));
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const elderOptions = elders.map((elder) => ({ value: elder.name, label: elder.name }));

  const handleSend = async () => {
    const text = input.trim();
    if (!text || loading) {
      return;
    }
    const assistantIndex = messages.length + 1;
    const next: ChatMessage[] = [
      ...messages,
      { role: 'user', content: text },
      { role: 'assistant', content: '' }
    ];
    setMessages(next);
    setInput('');
    setLoading(true);
    try {
      await streamAgentMessage(text, (token) => {
        setMessages((current) =>
          current.map((message, index) =>
            index === assistantIndex ? { ...message, content: message.content + token } : message
          )
        );
      });
    } catch (error) {
      setMessages((current) => current.filter((_, index) => index !== assistantIndex));
      antdMessage.error(error instanceof Error ? error.message : '请求失败');
    } finally {
      setLoading(false);
    }
  };

  const handleRecommend = async () => {
    if (!recommendElderName) {
      antdMessage.warning('请先选择老人');
      return;
    }
    setRecommendLoading(true);
    try {
      const data = await requestCheckInRecommendation(recommendElderName);
      setRecommendation(data.suggestion);
    } catch (error) {
      antdMessage.error(error instanceof Error ? error.message : '请求失败');
    } finally {
      setRecommendLoading(false);
    }
  };

  const handleCarePlan = async () => {
    if (!carePlanElderName) {
      antdMessage.warning('请先选择老人');
      return;
    }
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
    if (!alertId) {
      antdMessage.warning('请输入告警 ID');
      return;
    }
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
        <Title level={3}>智能助手</Title>
        <Paragraph>
          基于养老业务数据，提供健康风险画像、入住推荐、护理计划与告警分析等 Agent 能力。可在「养老业务」页对告警一键分析。
        </Paragraph>
        <Text type={health === 'ok' ? 'success' : 'secondary'}>后端状态：{health}</Text>
      </Card>

      <HealthProfileCard elders={elders} />

      <AdmissionCard elders={elders} />

      <Card title="入住推荐">
        <Space direction="vertical" style={{ width: '100%' }}>
          <Select
            showSearch
            placeholder="选择老人"
            style={{ width: '100%' }}
            optionFilterProp="label"
            options={elderOptions}
            value={recommendElderName}
            onChange={setRecommendElderName}
          />
          <Button type="primary" loading={recommendLoading} onClick={handleRecommend}>
            生成入住建议
          </Button>
          {recommendation ? <Card type="inner">{recommendation}</Card> : null}
        </Space>
      </Card>

      <Card title="护理计划生成">
        <Space direction="vertical" style={{ width: '100%' }}>
          <Select
            showSearch
            placeholder="选择老人"
            style={{ width: '100%' }}
            optionFilterProp="label"
            options={elderOptions}
            value={carePlanElderName}
            onChange={setCarePlanElderName}
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
            placeholder="输入告警 ID（可在「养老业务」页告警列表中查看）"
            onChange={(event) => setAlertId(event.target.value)}
          />
          <Button type="primary" loading={alertLoading} onClick={handleAlertAnalysis}>
            生成告警分析
          </Button>
          {alertAnalysis ? <Card type="inner">{alertAnalysis}</Card> : null}
        </Space>
      </Card>

      <Card title="Agent 对话" className="chat-card">
        <div className="chat-window">
          {messages.length === 0 ? (
            <div className="chat-empty">
              <RobotOutlined style={{ fontSize: 32, color: '#bfbfbf' }} />
              <Text type="secondary">向智能助手提问，例如「张桂兰老人近期需要注意什么？」</Text>
            </div>
          ) : null}
          {messages.map((msg, index) => (
            <div key={index} className={`chat-bubble chat-bubble-${msg.role}`}>
              <div className="chat-bubble-avatar">
                {msg.role === 'user' ? <TeamOutlined /> : <RobotOutlined />}
              </div>
              <div className="chat-bubble-content">
                {msg.content || (msg.role === 'assistant' && loading ? '正在思考...' : '')}
              </div>
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>
        <Input.TextArea
          value={input}
          rows={3}
          placeholder="输入消息，Ctrl/⌘ + Enter 发送"
          onChange={(event) => setInput(event.target.value)}
          onPressEnter={(event) => {
            if (event.ctrlKey || event.metaKey) {
              handleSend();
            }
          }}
        />
        <div style={{ marginTop: 8, textAlign: 'right' }}>
          <Button type="primary" loading={loading} onClick={handleSend}>
            发送
          </Button>
        </div>
      </Card>
    </Space>
  );

  if (embedded) {
    return content;
  }

  return <div style={{ minHeight: '100vh', padding: 32, background: '#f5f7fb' }}>{content}</div>;
}
