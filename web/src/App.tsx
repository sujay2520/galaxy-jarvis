import { Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import Layout from './components/Layout';
import ChatView from './components/ChatView';
import AgentsDashboard from './components/AgentsDashboard';
import AuditLog from './components/AuditLog';
import SettingsView from './components/SettingsView';
import ConversationHistory from './components/ConversationHistory';

function App() {
  return (
    <ThemeProvider>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<ChatView />} />
          <Route path="agents" element={<AgentsDashboard />} />
          <Route path="audit" element={<AuditLog />} />
          <Route path="settings" element={<SettingsView />} />
          <Route path="conversations" element={<ConversationHistory />} />
        </Route>
      </Routes>
    </ThemeProvider>
  );
}

export default App;
