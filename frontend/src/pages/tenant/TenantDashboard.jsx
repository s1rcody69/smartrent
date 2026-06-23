import DashboardLayout from '../../components/layout/DashboardLayout'

const navLinks = [
  { path: '/tenant/dashboard', label: 'Overview' },
  { path: '/tenant/lease', label: 'My Lease' },
  { path: '/tenant/maintenance', label: 'Maintenance' },
  { path: '/tenant/payments', label: 'Payments' },
]

function TenantDashboard() {
  return (
    <DashboardLayout navLinks={navLinks}>
      <h1 className="text-2xl font-bold text-slate-900">Welcome back</h1>
      <p className="text-slate-500 mt-1">Your lease and payment overview will go here.</p>
    </DashboardLayout>
  )
}

export default TenantDashboard