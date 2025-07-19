import { useState } from 'react';
import { Cpu, FileText, Sliders, Plug } from 'lucide-react';
import SimpleLayout from '../../components/common/SimpleLayout';
import ModelConfig from './components/ModelConfig';
import PromptEngineering from './components/PromptEngineering';
import AnalysisParameters from './components/AnalysisParameters';
import PluginManagement from './components/PluginManagement';
import './AdminApp.css';

const navItems = [
  { id: 'models', label: 'Model Configuration', icon: Cpu, component: ModelConfig },
  { id: 'prompts', label: 'Prompt Engineering', icon: FileText, component: PromptEngineering },
  { id: 'parameters', label: 'Analysis Parameters', icon: Sliders, component: AnalysisParameters },
  { id: 'plugins', label: 'Plugin Management', icon: Plug, component: PluginManagement },
];

export default function AdminApp() {
  const [activeSection, setActiveSection] = useState('models');

  const ActiveComponent = navItems.find(item => item.id === activeSection)?.component || ModelConfig;


  return (
    <SimpleLayout>
      <aside className="admin-sidebar">
        {navItems.map(item => {
          const Icon = item.icon;
          return (
            <div
              key={item.id}
              className={`nav-item ${activeSection === item.id ? 'active' : ''}`}
              onClick={() => setActiveSection(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </div>
          );
        })}
      </aside>
      
      <main className="admin-content">
        <ActiveComponent />
      </main>
    </SimpleLayout>
  );
}