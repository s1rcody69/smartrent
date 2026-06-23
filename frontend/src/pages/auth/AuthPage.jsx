import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useDispatch } from 'react-redux'
import { useLoginMutation, useRegisterMutation } from '../../features/auth/authApi'
import { setCredentials } from '../../features/auth/authSlice'

function AuthPage() {
  const [mode, setMode] = useState('login') // 'login' | 'register'
  const navigate = useNavigate()
  const dispatch = useDispatch()

  const [login, { isLoading: loginLoading, error: loginError }] = useLoginMutation()
  const [register, { isLoading: registerLoading, error: registerError }] = useRegisterMutation()

  const [form, setForm] = useState({
    email: '',
    password: '',
    confirm_password: '',
    first_name: '',
    last_name: '',
    phone_number: '',
    role: 'tenant',
  })

  const isLoading = loginLoading || registerLoading
  const error = mode === 'login' ? loginError : registerError

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const redirectByRole = (role) => {
    if (role === 'admin') navigate('/admin/dashboard')
    else if (role === 'landlord') navigate('/landlord/dashboard')
    else navigate('/tenant/dashboard')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (mode === 'login') {
        const response = await login({
          email: form.email,
          password: form.password,
        }).unwrap()
        dispatch(setCredentials(response))
        redirectByRole(response.user.role)
      } else {
        const response = await register(form).unwrap()
        dispatch(setCredentials(response))
        redirectByRole(response.user.role)
      }
    } catch (err) {
      console.error(`${mode} failed:`, err)
    }
  }

  const errorMessage = () => {
    if (!error) return null
    if (error.data?.error) return error.data.error
    if (error.data) {
      const firstField = Object.keys(error.data)[0]
      const firstMsg = error.data[firstField]
      return Array.isArray(firstMsg) ? firstMsg[0] : firstMsg
    }
    return 'Something went wrong. Please try again.'
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center px-4 py-12">

      <Link to="/" className="text-2xl font-bold text-slate-900 mb-8 tracking-tight">
        SmartRent
      </Link>

      <div className="w-full max-w-md bg-white rounded-2xl border border-slate-200 shadow-sm p-8">

        {/* Toggle pill */}
        <div className="flex bg-slate-100 rounded-full p-1 mb-8">
          <button
            type="button"
            onClick={() => setMode('login')}
            className={`flex-1 py-2 rounded-full text-sm font-medium transition-colors ${
              mode === 'login'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-500'
            }`}
          >
            Log in
          </button>
          <button
            type="button"
            onClick={() => setMode('register')}
            className={`flex-1 py-2 rounded-full text-sm font-medium transition-colors ${
              mode === 'register'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-500'
            }`}
          >
            Sign up
          </button>
        </div>

        <h1 className="text-2xl font-semibold text-slate-900 mb-1">
          {mode === 'login' ? 'Welcome back' : 'Create your account'}
        </h1>
        <p className="text-sm text-slate-500 mb-6">
          {mode === 'login'
            ? 'Log in to manage your properties or lease.'
            : 'Get started with SmartRent in a few steps.'}
        </p>

        {errorMessage() && (
          <div className="bg-red-50 border border-red-100 text-red-700 text-sm rounded-lg px-4 py-3 mb-5">
            {errorMessage()}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">

          {mode === 'register' && (
            <>
              {/* Role selector — two clickable cards */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  I am a
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setForm({ ...form, role: 'landlord' })}
                    className={`rounded-xl border px-4 py-3 text-sm font-medium text-left transition-colors ${
                      form.role === 'landlord'
                        ? 'border-amber-600 bg-amber-50 text-amber-800'
                        : 'border-slate-200 text-slate-600 hover:border-slate-300'
                    }`}
                  >
                    Landlord
                  </button>
                  <button
                    type="button"
                    onClick={() => setForm({ ...form, role: 'tenant' })}
                    className={`rounded-xl border px-4 py-3 text-sm font-medium text-left transition-colors ${
                      form.role === 'tenant'
                        ? 'border-amber-600 bg-amber-50 text-amber-800'
                        : 'border-slate-200 text-slate-600 hover:border-slate-300'
                    }`}
                  >
                    Tenant
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">First name</label>
                  <input
                    name="first_name"
                    value={form.first_name}
                    onChange={handleChange}
                    required
                    className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Last name</label>
                  <input
                    name="last_name"
                    value={form.last_name}
                    onChange={handleChange}
                    required
                    className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Phone number</label>
                <input
                  name="phone_number"
                  value={form.phone_number}
                  onChange={handleChange}
                  placeholder="0712345678"
                  className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>
            </>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              required
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              required
              minLength={8}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500"
            />
          </div>

          {mode === 'register' && (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Confirm password</label>
              <input
                type="password"
                name="confirm_password"
                value={form.confirm_password}
                onChange={handleChange}
                required
                minLength={8}
                className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500"
              />
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-amber-600 text-white py-2.5 rounded-full font-medium text-sm hover:bg-amber-700 transition-colors disabled:opacity-50 mt-2"
          >
            {isLoading
              ? mode === 'login' ? 'Logging in...' : 'Creating account...'
              : mode === 'login' ? 'Log in' : 'Create account'}
          </button>
        </form>
      </div>

      <Link to="/" className="text-sm text-slate-500 mt-6 hover:text-slate-700">
        ← Back to home
      </Link>
    </div>
  )
}

export default AuthPage