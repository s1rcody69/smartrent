import DashboardLayout from '../../components/layout/DashboardLayout'

const navLinks = [
  { path: '/admin/dashboard', label: 'Overview' },
  { path: '/admin/users', label: 'Users' },
  { path: '/admin/properties', label: 'Properties' },
]

function AdminDashboard() {
  return (
    <DashboardLayout navLinks={navLinks}>
      <h1 className="text-2xl font-bold text-slate-900">Admin Overview</h1>
      <p className="text-slate-500 mt-1">Platform-wide stats will go here.</p>
    </DashboardLayout>
  )
}

export default AdminDashboard