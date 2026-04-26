import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import MerchantDashboard from './pages/MerchantDashboard';
import KYCForm from './pages/KYCForm';
import ReviewerDashboard from './pages/ReviewerDashboard';
import SubmissionDetail from './pages/SubmissionDetail';

function App() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-surface-950">
      {user && <Navbar />}
      <main className={user ? 'pt-4 pb-12' : ''}>
        <Routes>
          {/* Public */}
          <Route
            path="/login"
            element={user ? <Navigate to="/" replace /> : <LoginPage />}
          />

          {/* Merchant routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute role="merchant">
                <MerchantDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/kyc/new"
            element={
              <ProtectedRoute role="merchant">
                <KYCForm />
              </ProtectedRoute>
            }
          />
          <Route
            path="/kyc/:id/edit"
            element={
              <ProtectedRoute role="merchant">
                <KYCForm />
              </ProtectedRoute>
            }
          />
          <Route
            path="/submissions/:id"
            element={
              <ProtectedRoute>
                <SubmissionDetail />
              </ProtectedRoute>
            }
          />

          {/* Reviewer routes */}
          <Route
            path="/reviewer"
            element={
              <ProtectedRoute role="reviewer">
                <ReviewerDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/reviewer/submissions/:id"
            element={
              <ProtectedRoute role="reviewer">
                <SubmissionDetail reviewer />
              </ProtectedRoute>
            }
          />

          {/* Catch-all */}
          <Route path="*" element={<Navigate to={user ? '/' : '/login'} replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
