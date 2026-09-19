import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import ChatView from './components/ChatView';
import AgentsDashboard from './components/AgentsDashboard';
import PermissionsManager from './components/PermissionsManager';
import ApprovalQueue from './components/ApprovalQueue';
import AuditLog from './components/AuditLog';
import SettingsView from './components/SettingsView';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<ChatView />} />
        <Route path="agents" element={<AgentsDashboard />} />
        <Route path="permissions" element={<PermissionsManager />} />
        <Route path="approvals" element={<ApprovalQueue />} />
        <Route path="audit" element={<AuditLog />} />
        <Route path="settings" element={<SettingsView />} />
      </Route>
    </Routes>
  );
}

export default App;
