import { RobotOutlined, TeamOutlined } from '@ant-design/icons';
import { Layout, Menu, theme } from 'antd';
import { useState } from 'react';

import { AgentHomePage } from './AgentHomePage';
import { NursingDashboardPage } from './NursingDashboardPage';

const { Header, Sider, Content } = Layout;

type PageKey = 'nursing' | 'agent';

export function AppShell() {
  const [page, setPage] = useState<PageKey>('nursing');
  const { token } = theme.useToken();

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider breakpoint="lg" collapsedWidth="0">
        <div className="app-logo">ZZYL Agent</div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[page]}
          onClick={(event) => setPage(event.key as PageKey)}
          items={[
            { key: 'nursing', icon: <TeamOutlined />, label: '养老业务' },
            { key: 'agent', icon: <RobotOutlined />, label: '智能助手' }
          ]}
        />
      </Sider>
      <Layout>
        <Header style={{ background: token.colorBgContainer, fontSize: 18, fontWeight: 600 }}>
          智慧养老单体 Agent 平台
        </Header>
        <Content style={{ margin: 24 }}>
          {page === 'nursing' ? <NursingDashboardPage /> : <AgentHomePage embedded />}
        </Content>
      </Layout>
    </Layout>
  );
}
