import { Alert, Button, Card, Col, Form, Input, Row, Select, Space, Statistic, Table, Tag, Typography, message } from 'antd';
import { useEffect, useState } from 'react';

import {
  type AlertRecord,
  type Bed,
  type Elder,
  type NursingProject,
  type Room,
  createAlert,
  createElder,
  listAlerts,
  listBeds,
  listElders,
  listNursingProjects,
  listRooms,
  seedDemoData
} from '../api/nursing';

const { Title, Paragraph } = Typography;

export function NursingDashboardPage() {
  const [elderForm] = Form.useForm();
  const [alertForm] = Form.useForm();
  const [elders, setElders] = useState<Elder[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [beds, setBeds] = useState<Bed[]>([]);
  const [projects, setProjects] = useState<NursingProject[]>([]);
  const [alerts, setAlerts] = useState<AlertRecord[]>([]);
  const [error, setError] = useState('');
  const [seeding, setSeeding] = useState(false);

  const loadData = () => {
    Promise.all([listElders(), listRooms(), listBeds(), listNursingProjects(), listAlerts()])
      .then(([elderData, roomData, bedData, projectData, alertData]) => {
        setElders(elderData);
        setRooms(roomData);
        setBeds(bedData);
        setProjects(projectData);
        setAlerts(alertData);
        setError('');
      })
      .catch((loadError) => setError(loadError instanceof Error ? loadError.message : '加载失败'));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSeedDemoData = async () => {
    setSeeding(true);
    try {
      await seedDemoData();
      message.success('演示数据已准备好');
      loadData();
    } catch (seedError) {
      message.error(seedError instanceof Error ? seedError.message : '初始化失败');
    } finally {
      setSeeding(false);
    }
  };

  const handleCreateElder = async (values: {
    name: string;
    gender?: string;
    phone?: string;
    family_contact?: string;
    health_summary?: string;
  }) => {
    await createElder({ ...values, gender: values.gender || 'unknown' });
    message.success('老人档案已保存');
    elderForm.resetFields();
    loadData();
  };

  const handleCreateAlert = async (values: {
    elder_id?: number;
    device_name: string;
    severity?: string;
    content: string;
  }) => {
    await createAlert({ ...values, severity: values.severity || 'medium' });
    message.success('告警记录已保存');
    alertForm.resetFields();
    loadData();
  };

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Card>
        <Title level={3}>养老业务总览</Title>
        <Paragraph>
          这里承接原系统中的老人档案、房间床位、护理项目和告警数据，后续会接入入住推荐、护理计划和告警分析 Agent。
        </Paragraph>
        <Button type="primary" loading={seeding} onClick={handleSeedDemoData}>
          初始化演示数据
        </Button>
        {error ? <Alert type="warning" message={error} showIcon style={{ marginTop: 16 }} /> : null}
      </Card>

      <Row gutter={[16, 16]}>
        <Col xs={24} md={12} lg={6}>
          <Card><Statistic title="老人档案" value={elders.length} suffix="人" /></Card>
        </Col>
        <Col xs={24} md={12} lg={6}>
          <Card><Statistic title="房间" value={rooms.length} suffix="间" /></Card>
        </Col>
        <Col xs={24} md={12} lg={6}>
          <Card><Statistic title="床位" value={beds.length} suffix="张" /></Card>
        </Col>
        <Col xs={24} md={12} lg={6}>
          <Card><Statistic title="护理项目" value={projects.length} suffix="项" /></Card>
        </Col>
      </Row>

      <Card title="新增老人档案">
        <Form form={elderForm} layout="vertical" onFinish={handleCreateElder}>
          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Form.Item name="name" label="姓名" rules={[{ required: true, message: '请输入姓名' }]}>
                <Input placeholder="例如：张桂兰" />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="gender" label="性别" initialValue="unknown">
                <Select
                  options={[
                    { value: 'female', label: '女' },
                    { value: 'male', label: '男' },
                    { value: 'unknown', label: '未知' }
                  ]}
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="phone" label="联系电话">
                <Input placeholder="手机号" />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="family_contact" label="家属联系人">
                <Input placeholder="联系人姓名" />
              </Form.Item>
            </Col>
            <Col xs={24} md={16}>
              <Form.Item name="health_summary" label="健康摘要">
                <Input.TextArea rows={2} placeholder="慢病、跌倒风险、睡眠等摘要" />
              </Form.Item>
            </Col>
          </Row>
          <Button type="primary" htmlType="submit">保存老人档案</Button>
        </Form>
      </Card>

      <Card title="最新老人档案">
        <Table
          rowKey="id"
          dataSource={elders}
          pagination={false}
          columns={[
            { title: '姓名', dataIndex: 'name' },
            { title: '性别', dataIndex: 'gender' },
            { title: '联系电话', dataIndex: 'phone' },
            { title: '家属联系人', dataIndex: 'family_contact' },
            { title: '健康摘要', dataIndex: 'health_summary' }
          ]}
        />
      </Card>

      <Card title="新增告警记录">
        <Form form={alertForm} layout="vertical" onFinish={handleCreateAlert}>
          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Form.Item name="elder_id" label="关联老人">
                <Select
                  allowClear
                  placeholder="选择老人"
                  options={elders.map((elder) => ({ value: elder.id, label: elder.name }))}
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="device_name" label="设备名称" rules={[{ required: true, message: '请输入设备名称' }]}>
                <Input placeholder="例如：智能床垫 A-301" />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="severity" label="告警级别" initialValue="medium">
                <Select
                  options={[
                    { value: 'low', label: '低' },
                    { value: 'medium', label: '中' },
                    { value: 'high', label: '高' },
                    { value: 'critical', label: '紧急' }
                  ]}
                />
              </Form.Item>
            </Col>
            <Col span={24}>
              <Form.Item name="content" label="告警内容" rules={[{ required: true, message: '请输入告警内容' }]}>
                <Input.TextArea rows={2} placeholder="描述设备告警内容" />
              </Form.Item>
            </Col>
          </Row>
          <Button type="primary" htmlType="submit">保存告警记录</Button>
        </Form>
      </Card>

      <Card title="告警记录">
        <Table
          rowKey="id"
          dataSource={alerts}
          pagination={false}
          columns={[
            { title: '设备', dataIndex: 'device_name' },
            {
              title: '级别',
              dataIndex: 'severity',
              render: (severity: string) => <Tag color={severity === 'critical' ? 'red' : 'orange'}>{severity}</Tag>
            },
            { title: '内容', dataIndex: 'content' },
            { title: '状态', dataIndex: 'handled', render: (handled: boolean) => (handled ? '已处理' : '待处理') }
          ]}
        />
      </Card>
    </Space>
  );
}
