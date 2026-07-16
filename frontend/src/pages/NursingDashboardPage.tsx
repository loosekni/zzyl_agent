import { Alert, Button, Card, Col, Row, Space, Statistic, Table, Tag, Typography, message } from 'antd';
import { useEffect, useState } from 'react';

import {
  type AlertRecord,
  type Bed,
  type Elder,
  type NursingProject,
  type Room,
  listAlerts,
  listBeds,
  listElders,
  listNursingProjects,
  listRooms,
  seedDemoData
} from '../api/nursing';

const { Title, Paragraph } = Typography;

export function NursingDashboardPage() {
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
