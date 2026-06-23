import DashboardLayout from '../../components/layout/DashboardLayout'

const navLinks = [
  { path: '/landlord/dashboard', label: 'Overview' },
  { path: '/landlord/properties', label: 'Properties' },
  { path: '/landlord/leases', label: 'Leases' },
  { path: '/landlord/maintenance', label: 'Maintenance' },
  { path: '/landlord/payments', label: 'Payments' },
]

function LandlordDashboard() {
  return (
    <DashboardLayout navLinks={navLinks}>
      <h1 className="text-2xl font-bold text-slate-900">Welcome back</h1>
      <p className="text-slate-500 mt-1">Your property overview will go here.</p>
    </DashboardLayout>
  )
}

export default LandlordDashboard