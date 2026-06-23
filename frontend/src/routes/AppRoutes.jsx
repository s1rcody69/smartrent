import { Routes, Route } from 'react-router-dom'
import Landing from '../pages/public/Landing'
import AuthPage from '../pages/auth/AuthPage'
import ProtectedRoute from './ProtectedRoute'
import AdminDashboard from '../pages/admin/AdminDashboard'
import LandlordDashboard from '../pages/landlord/LandlordDashboard'
import TenantDashboard from '../pages/tenant/TenantDashboard'

function AppRoutes() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<AuthPage />} />
      <Route path="/register" element={<AuthPage />} />

      {/* Protected — role scoped */}
      <Route
        path="/admin/dashboard"
        element={
          <ProtectedRoute allowedRoles={['admin']}>
            <AdminDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/landlord/dashboard"
        element={
          <ProtectedRoute allowedRoles={['landlord']}>
            <LandlordDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/tenant/dashboard"
        element={
          <ProtectedRoute allowedRoles={['tenant']}>
            <TenantDashboard />
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}

export default AppRoutes