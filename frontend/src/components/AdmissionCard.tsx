import { Button, Card, Select, Space, Statistic, Tag, Typography, message } from 'antd';
import { useEffect, useState } from 'react';

import {
  requestAdmissionCancel,
  requestAdmissionConfirm,
  requestAdmissionPreview,
  type AdmissionPreview
} from '../api/agent';
import { type Elder } from '../api/nursing';

const { Text, Paragraph } = Typography;

interface AdmissionCardProps {
  elders: Elder[];
}

export function AdmissionCard({ elders }: AdmissionCardProps) {
  const [elderId, setElderId] = useState<number | undefined>(undefined);
  const [preview, setPreview] = useState<AdmissionPreview | null>(null);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [result, setResult] = useState('');
  const [remaining, setRemaining] = useState<number | null>(null);

  useEffect(() => {
    if (!preview) {
      setRemaining(null);
      return;
    }
    const update = () => {
      const expires = new Date(preview.expires_at).getTime();
      const left = Math.max(0, Math.floor((expires - Date.now()) / 1000));
      setRemaining(left);
    };
    update();
    const timer = setInterval(update, 1000);
    return () => clearInterval(timer);
  }, [preview]);

  const handlePreview = async () => {
    if (elderId === undefined) {
      message.warning('请先选择老人');
      return;
    }
    setLoading(true);
    setResult('');
    try {
      const data = await requestAdmissionPreview(elderId);
      setPreview(data);
    } catch (error) {
      message.error(error instanceof Error ? error.message : '预览失败');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!preview) {
      return;
    }
    setActionLoading(true);
    try {
      const data = await requestAdmissionConfirm(preview.run_id, preview.reservation_token);
      setResult(data.message);
      setPreview(null);
      message.success('入住已确认');
    } catch (error) {
      message.error(error instanceof Error ? error.message : '确认失败');
    } finally {
      setActionLoading(false);
    }
  };

  const handleCancel = async () => {
    if (!preview) {
      return;
    }
    setActionLoading(true);
    try {
      const data = await requestAdmissionCancel(preview.run_id, preview.reservation_token);
      setResult(data.message);
      setPreview(null);
    } catch (error) {
      message.error(error instanceof Error ? error.message : '取消失败');
    } finally {
      setActionLoading(false);
    }
  };

  const expired = remaining !== null && remaining <= 0;

  return (
    <Card title="入住办理（Agent 闭环）">
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <Space wrap>
          <Select
            showSearch
            placeholder="选择老人"
            style={{ width: 220 }}
            optionFilterProp="label"
            options={elders.map((elder) => ({ value: elder.id, label: elder.name }))}
            onChange={setElderId}
          />
          <Button type="primary" loading={loading} onClick={handlePreview}>
            生成入住预览
          </Button>
        </Space>

        {preview ? (
          <Card type="inner" title={`预览 #${preview.run_id} - ${preview.elder_name}`}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Tag color="processing">{preview.status}</Tag>
                <Text>拟入住床位：</Text>
                <Tag color="blue">{preview.bed_no}</Tag>
              </div>
              <Paragraph style={{ margin: 0 }}>{preview.preview_summary}</Paragraph>
              <div>
                <Text type="secondary">Reservation Token：</Text>
                <Text code style={{ fontSize: 12 }}>
                  {preview.reservation_token}
                </Text>
              </div>
              <div>
                {expired ? (
                  <Tag color="red">已过期，请重新生成预览</Tag>
                ) : (
                  <Statistic
                    title="确认剩余时间"
                    value={remaining ?? 0}
                    suffix="秒"
                    valueStyle={{
                      color: (remaining ?? 0) < 60 ? '#fa8c16' : '#52c41a'
                    }}
                  />
                )}
              </div>
              <Space>
                <Button
                  type="primary"
                  loading={actionLoading}
                  disabled={expired}
                  onClick={handleConfirm}
                >
                  确认入住
                </Button>
                <Button loading={actionLoading} disabled={expired} onClick={handleCancel}>
                  取消
                </Button>
              </Space>
            </Space>
          </Card>
        ) : null}

        {result ? <Text type="success">{result}</Text> : null}

        <Text type="secondary" style={{ fontSize: 12 }}>
          迁移自原项目 AdmissionAgent：preview 生成限时 reservation token → WAITING_APPROVAL → 人工确认/取消。
        </Text>
      </Space>
    </Card>
  );
}
