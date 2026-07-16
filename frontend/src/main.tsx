import 'antd/dist/reset.css';

import React from 'react';
import ReactDOM from 'react-dom/client';

import { AgentHomePage } from './pages/AgentHomePage';
import './styles.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AgentHomePage />
  </React.StrictMode>
);
