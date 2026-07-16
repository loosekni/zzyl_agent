import { Alert, Button, Card, Col, Form, Input, Row, Select, Space, Statistic, Table, Tag, Typography, message } from 'antd';
import { useEffect, useState } from 'react';

import {
  type AlertRecord,
  type Bed,
  type Elder,
  type NursingProject,
  type Room,
  createAlert,
  createBed,
  createElder,
  createNursingProject,
  createRoom,
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
  const [projectForm] = Form.useForm();
  const [roomForm] = Form.useForm();
  const [bedForm] = Form.useForm();
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

  const handleCreateProject = async (values: {
    name: string;
    category?: string;
    description?: string;
    price?: number;
  }) => {
    await createNursingProject({
      name: values.name,
      category: values.category || 'daily',
      description: values.description,
      price: Number(values.price || 0)
    });
    message.success('护理项目已保存');
    projectForm.resetFields();
    loadData();
  };

  const handleCreateRoom = async (values: { floor: string; room_no: string; room_type?: string }) => {
    await createRoom({ ...values, room_type: values.room_type || 'standard' });
    message.success('房间已保存');
    roomForm.resetFields();
    loadData();
  };

  const handleCreateBed = async (values: { room_id: number; bed_no: string; status?: string }) => {
    await createBed({ ...values, status: values.status || 'available' });
    message.success('床位已保存');
    bedForm.resetFields();
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

      <Card title="新增房间和床位">
        <Row gutter={24}>
          <Col xs={24} lg={12}>
            <Form form={roomForm} layout="vertical" onFinish={handleCreateRoom}>
              <Row gutter={16}>
                <Col xs={24} md={8}>
                  <Form.Item name="floor" label="楼层" rules={[{ required: true, message: '请输入楼层' }]}>
                    <Input placeholder="例如：3F" />
                  </Form.Item>
                </Col>
                <Col xs={24} md={8}>
                  <Form.Item name="room_no" label="房间号" rules={[{ required: true, message: '请输入房间号' }]}>
                    <Input placeholder="例如：301" />
                  </Form.Item>
                </Col>
                <Col xs={24} md={8}>
                  <Form.Item name="room_type" label="房型" initialValue="standard">
                    <Select
                      options={[
                        { value: 'standard', label: '标准房' },
                        { value: 'care', label: '护理房' },
                        { value: 'vip', label: 'VIP 房' }
                      ]}
                    />
                  </Form.Item>
                </Col>
              </Row>
              <Button type="primary" htmlType="submit">保存房间</Button>
            </Form>
          </Col>
          <Col xs={24} lg={12}>
            <Form form={bedForm} layout="vertical" onFinish={handleCreateBed}>
              <Row gutter={16}>
                <Col xs={24} md={10}>
                  <Form.Item name="room_id" label="所属房间" rules={[{ required: true, message: '请选择房间' }]}>
                    <Select
                      placeholder="选择房间"
                      options={rooms.map((room) => ({ value: room.id, label: `${room.floor}-${room.room_no}` }))}
                    />
                  </Form.Item>
                </Col>
                <Col xs={24} md={8}>
                  <Form.Item name="bed_no" label="床位号" rules={[{ required: true, message: '请输入床位号' }]}>
                    <Input placeholder="例如：301-1" />
                  </Form.Item>
                </Col>
                <Col xs={24} md={6}>
                  <Form.Item name="status" label="状态" initialValue="available">
                    <Select
                      options={[
                        { value: 'available', label: '可用' },
                        { value: 'occupied', label: '已入住' },
                        { value: 'maintenance', label: '维护中' }
                      ]}
                    />
                  </Form.Item>
                </Col>
              </Row>
              <Button type="primary" htmlType="submit">保存床位</Button>
            </Form>
          </Col>
        </Row>
      </Card>

      <Card title="房间与床位">
        <Table
          rowKey="id"
          dataSource={beds}
          pagination={false}
          columns={[
            { title: '床位号', dataIndex: 'bed_no' },
            { title: '房间 ID', dataIndex: 'room_id' },
            { title: '状态', dataIndex: 'status' }
          ]}
        />
      </Card>

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

      <Card title="新增护理项目">
        <Form form={projectForm} layout="vertical" onFinish={handleCreateProject}>
          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Form.Item name="name" label="项目名称" rules={[{ required: true, message: '请输入项目名称' }]}>
                <Input placeholder="例如：血压监测" />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="category" label="项目类型" initialValue="daily">
                <Select
                  options={[
                    { value: 'daily', label: '日常照护' },
                    { value: 'medical', label: '医疗护理' },
                    { value: 'safety', label: '安全巡护' },
                    { value: 'rehab', label: '康复训练' }
                  ]}
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="price" label="价格">
                <Input type="number" placeholder="0" />
              </Form.Item>
            </Col>
            <Col span={24}>
              <Form.Item name="description" label="项目说明">
                <Input.TextArea rows={2} placeholder="描述护理内容和执行要求" />
              </Form.Item>
            </Col>
          </Row>
          <Button type="primary" htmlType="submit">保存护理项目</Button>
        </Form>
      </Card>

      <Card title="护理项目">
        <Table
          rowKey="id"
          dataSource={projects}
          pagination={false}
          columns={[
            { title: '项目名称', dataIndex: 'name' },
            { title: '类型', dataIndex: 'category' },
            { title: '价格', dataIndex: 'price' }
          ]}
        />
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
