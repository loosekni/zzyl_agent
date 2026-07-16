import { Button, Card, Col, Empty, Progress, Row, Select, Space, Spin, Statistic, Tag, Typography, message } from 'antd';
import { useState } from 'react';

import { requestHealthProfile, type HealthProfile } from '../api/agent';
import { type Elder } from '../api/nursing';

const { Paragraph, Text } = Typography;

const levelColor: Record<string, string> = {
  '极高': '#f5222d',
  '高': '#fa8c16',
  '中': '#faad14',
  '低': '#52c41a',
  '未知': '#8c8c8c'
};

const severityColor: Record<string, string> = {
  critical: 'red',
  high: 'orange',
  medium: 'gold',
  low: 'green'
};

const severityLabel: Record<string, string> = {
  critical: '紧急',
  high: '高',
  medium: '中',
  low: '低'
};

interface HealthProfileCardProps {
  elders: Elder[];
}

export function HealthProfileCard({ elders }: HealthProfileCardProps) {
  const [elderId, setElderId] = useState<number | undefined>(undefined);
  const [profile, setProfile] = useState<HealthProfile | null>(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    if (elderId === undefined) {
      message.warning('请先选择老人');
      return;
    }
    setLoading(true);
    try {
      const data = await requestHealthProfile(elderId);
      setProfile(data);
    } catch (error) {
      message.error(error instanceof Error ? error.message : '生成失败');
    } finally {
      setLoading(false);
    }
  };

  const scoreColor = profile ? levelColor[profile.risk_level] ?? '#8c8c8c' : '#8c8c8c';

  return (
    <Card title="老人健康风险画像">
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <Space wrap>
          <Select
            showSearch
            placeholder="选择老人"
            style={{ width: 220 }}
            optionFilterProp="label"
            options={elders.map((elder) => ({ value: elder.id, label: elder.name }))}
            onChange={(value) => setElderId(value)}
          />
          <Button type="primary" loading={loading} onClick={handleGenerate}>
            生成画像
          </Button>
        </Space>

        {loading ? <Spin /> : null}

        {profile && !loading ? (
          <>
            <Row gutter={[24, 24]} align="middle">
              <Col xs={24} md={8} style={{ textAlign: 'center' }}>
                <Progress
                  type="dashboard"
                  percent={profile.risk_score}
                  strokeColor={scoreColor}
                  format={() => `${profile.risk_score}分`}
                />
                <div style={{ marginTop: 8 }}>
                  <Tag color={scoreColor} style={{ fontSize: 14, padding: '2px 12px' }}>
                    风险等级：{profile.risk_level}
                  </Tag>
                </div>
              </Col>
              <Col xs={24} md={16}>
                <Row gutter={[16, 16]}>
                  <Col span={8}>
                    <Statistic title="累计告警" value={profile.alert_total} suffix="次" />
                  </Col>
                  <Col span={16}>
                    <Text type="secondary">告警级别分布</Text>
                    <div style={{ marginTop: 8 }}>
                      {profile.alert_stats.length > 0
                        ? profile.alert_stats.map((stat) => (
                            <Tag
                              key={stat.severity}
                              color={severityColor[stat.severity]}
                              style={{ marginRight: 8 }}
                            >
                              {severityLabel[stat.severity] ?? stat.severity} {stat.count}次
                            </Tag>
                          ))
                        : <Text type="secondary">暂无告警</Text>}
                    </div>
                  </Col>
                </Row>
                <div style={{ marginTop: 16 }}>
                  <Text type="secondary">高频告警设备</Text>
                  <div style={{ marginTop: 8 }}>
                    {profile.top_devices.length > 0
                      ? profile.top_devices.map((device) => (
                          <Tag key={device.device_name} style={{ marginRight: 8 }}>
                            {device.device_name}（{device.count}次）
                          </Tag>
                        ))
                      : <Text type="secondary">暂无</Text>}
                  </div>
                </div>
                <div style={{ marginTop: 16 }}>
                  <Text type="secondary">推荐护理项目</Text>
                  <div style={{ marginTop: 8 }}>
                    {profile.recommended_projects.length > 0
                      ? profile.recommended_projects.map((project) => (
                          <Tag key={project} color="blue" style={{ marginRight: 8 }}>
                            {project}
                          </Tag>
                        ))
                      : <Text type="secondary">暂无推荐</Text>}
                  </div>
                </div>
              </Col>
            </Row>

            <Card type="inner" title="分析总结">
              <Paragraph style={{ whiteSpace: 'pre-wrap', margin: 0 }}>{profile.summary}</Paragraph>
            </Card>

            {profile.recent_alerts.length > 0 ? (
              <Card type="inner" title="最近告警">
                <Space direction="vertical" style={{ width: '100%' }}>
                  {profile.recent_alerts.map((alert, index) => (
                    <div key={`${alert.device_name}-${index}`}>
                      <Tag color={severityColor[alert.severity]}>
                        {severityLabel[alert.severity] ?? alert.severity}
                      </Tag>
                      <Text>{alert.device_name}：</Text>
                      <Text type="secondary">{alert.content}</Text>
                    </div>
                  ))}
                </Space>
              </Card>
            ) : null}
          </>
        ) : null}

        {!profile && !loading ? <Empty description="选择老人后生成健康风险画像" /> : null}
      </Space>
    </Card>
  );
}
