import { Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useAuthStore } from './store/authStore';

// Layout
import Layout from './components/layout/Layout';

// Pages
import Auth from './pages/Auth';
import DashboardSimple from './pages/DashboardSimple';
import Habits from './pages/Habits';
import HabitStats from './pages/HabitStats';
import HabitDetail from './pages/HabitDetail';
import BehaviorPatterns from './pages/BehaviorPatterns';
import Nutrition from './pages/Nutrition';
import HealthTracker from './pages/HealthTracker';
import HealthAssessment from './pages/HealthAssessment';
import { EmotionalSupportChat } from './pages/EmotionalSupportChat';
import Gamification from './pages/Gamification';
import { Chat } from './pages/Chat';
import Profile from './pages/Profile';

function App() {
  const { checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <Routes>
      <Route path="/login" element={<Auth />} />
      
      <Route
        path="/"
        element={
          <Layout>
            <Navigate to="/dashboard" replace />
          </Layout>
        }
      />
      
      <Route
        path="/dashboard"
        element={
          <Layout>
            <DashboardSimple />
          </Layout>
        }
      />
      
      <Route
        path="/habits"
        element={
          <Layout>
            <Habits />
          </Layout>
        }
      />
      
      <Route
        path="/habits-stats"
        element={
          <Layout>
            <HabitStats />
          </Layout>
        }
      />
      
      <Route
        path="/habits/:habitId/detail"
        element={
          <Layout>
            <HabitDetail />
          </Layout>
        }
      />
      
      <Route
        path="/habits/patterns"
        element={
          <Layout>
            <BehaviorPatterns />
          </Layout>
        }
      />
      
      <Route
        path="/nutrition"
        element={
          <Layout>
            <Nutrition />
          </Layout>
        }
      />
      
      <Route
        path="/health"
        element={
          <Layout>
            <HealthTracker />
          </Layout>
        }
      />
      
      <Route
        path="/health/assessment"
        element={
          <Layout>
            <HealthAssessment />
          </Layout>
        }
      />
      
      <Route
        path="/emotional"
        element={
          <Layout>
            <EmotionalSupportChat />
          </Layout>
        }
      />
      
      <Route
        path="/gamification"
        element={
          <Layout>
            <Gamification />
          </Layout>
        }
      />
      
      <Route
        path="/chat"
        element={
          <Layout>
            <Chat />
          </Layout>
        }
      />
      
      <Route
        path="/profile"
        element={
          <Layout>
            <Profile />
          </Layout>
        }
      />
      
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;