import { Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useAuthStore } from './store/authStore';

// Layout
import Layout from './components/layout/Layout';

// Pages
import Auth from './pages/Auth';
import Onboarding from './pages/Onboarding';
import DashboardSimple from './pages/DashboardSimple';
import DashboardV2 from './pages/DashboardV2';
import WaterTracker from './pages/WaterTracker';
import WeightTracker from './pages/WeightTracker';
import SleepTracker from './pages/SleepTracker';
import MeditationTracker from './pages/MeditationTracker';
import HabitManagement from './pages/HabitManagement';
import HabitCenter from './pages/HabitCenter';
import HabitRecords from './pages/HabitRecords';
import Habits from './pages/Habits';
import HabitStats from './pages/HabitStats';
import HabitDetail from './pages/HabitDetail';
import BehaviorPatterns from './pages/BehaviorPatterns';
import Nutrition from './pages/Nutrition';
import DietTracking from './pages/DietTracking';
import HealthTracker from './pages/HealthTracker';
import HealthAssessment from './pages/HealthAssessment';
import Gamification from './pages/Gamification';
import { Chat } from './pages/Chat';
import Profile from './pages/Profile';
import ExerciseCheckIn from './pages/ExerciseCheckIn';

function App() {
  const { checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <Routes>
      <Route path="/login" element={<Auth />} />
      
      <Route
        path="/onboarding"
        element={
          <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50">
            <Onboarding />
          </div>
        }
      />
      
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
            <DashboardV2 />
          </Layout>
        }
      />
      <Route
        path="/dashboard-simple"
        element={
          <Layout>
            <DashboardSimple />
          </Layout>
        }
      />
      <Route
        path="/dashboard-v2"
        element={
          <Layout>
            <DashboardV2 />
          </Layout>
        }
      />
      <Route
        path="/water-tracker"
        element={<WaterTracker />}
      />
      <Route
        path="/weight-tracker"
        element={<WeightTracker />}
      />
      <Route
        path="/sleep-tracker"
        element={<SleepTracker />}
      />
      <Route
        path="/meditation-tracker"
        element={<MeditationTracker />}
      />
      <Route
        path="/habit-management"
        element={<HabitManagement />}
      />
      <Route
        path="/habit-center"
        element={
          <Layout>
            <HabitCenter />
          </Layout>
        }
      />
      <Route
        path="/habit-records/:habitId"
        element={<HabitRecords />}
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
         path="/diet-tracking"
         element={
           <Layout>
             <DietTracking />
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
       
       <Route
         path="/exercise-checkin"
         element={
           <Layout>
             <ExerciseCheckIn />
           </Layout>
         }
       />
       
       <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;
// 系统管理后台路由
import AdminConfigs from './pages/admin/Configs';
