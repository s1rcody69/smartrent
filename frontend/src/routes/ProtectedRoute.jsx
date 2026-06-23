import { useSelector } from 'react-redux'
import { Navigate } from 'react-router-dom'

// allowedRoles is optional — if omitted, any logged-in user can access
function ProtectedRoute({ children, allowedRoles }) {
  const { user, accessToken } = useSelector((state) => state.auth)

  // Not logged in at all — send to login
  if (!accessToken || !user) {
    return <Navigate to="/login" replace />
  }

  // Logged in, but wrong role for this specific route
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/login" replace />
  }

  return children
}

export default ProtectedRoute