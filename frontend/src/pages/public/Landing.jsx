import { Link } from 'react-router-dom'

const FEATURED_PROPERTIES = [
  {
    id: 1,
    name: 'Sunset Apartments',
    location: 'Kilimani, Nairobi',
    price: '25,000',
    beds: 2,
    baths: 1,
    type: 'Apartment',
  },
  {
    id: 2,
    name: 'Riverside Heights',
    location: 'Westlands, Nairobi',
    price: '40,000',
    beds: 3,
    baths: 2,
    type: 'Apartment',
  },
  {
    id: 3,
    name: 'Garden Villa',
    location: 'Karen, Nairobi',
    price: '85,000',
    beds: 4,
    baths: 3,
    type: 'House',
  },
]

function Landing() {
  return (
    <div className="min-h-screen bg-slate-50">

      {/* Nav */}
      <nav className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <span className="text-xl font-bold text-slate-900 tracking-tight">SmartRent</span>
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
            <a href="#properties" className="hover:text-slate-900">Properties</a>
            <a href="#how-it-works" className="hover:text-slate-900">How it works</a>
          </div>
          <Link
            to="/login"
            className="bg-amber-600 text-white px-5 py-2 rounded-full text-sm font-medium hover:bg-amber-700 transition-colors"
          >
            Log in
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="bg-slate-900">
        <div className="max-w-7xl mx-auto px-6 py-20 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-white leading-tight max-w-3xl mx-auto">
            Property management, <span className="text-amber-500">simplified</span>
          </h1>
          <p className="text-slate-400 mt-4 max-w-xl mx-auto text-lg">
            Manage properties, leases, rent collection and maintenance — all from one platform built for landlords and tenants in Kenya.
          </p>
          <div className="mt-8 flex items-center justify-center gap-4">
            <Link
              to="/register"
              className="bg-amber-600 text-white px-6 py-3 rounded-full font-medium hover:bg-amber-700 transition-colors"
            >
              Get started
            </Link>
            
            <a
              href="#how-it-works"
              className="text-white border border-slate-700 px-6 py-3 rounded-full font-medium hover:bg-slate-800 transition-colors"
            >
              How it works
            </a>
          </div>
        </div>

        {/* Stat strip */}
        <div className="bg-slate-800 border-t border-slate-700">
          <div className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-3 gap-6 text-center">
            <div>
              <p className="text-3xl font-bold text-white">500+</p>
              <p className="text-sm text-slate-400 mt-1">Properties managed</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-white">1,200+</p>
              <p className="text-sm text-slate-400 mt-1">Happy tenants</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-white">98%</p>
              <p className="text-sm text-slate-400 mt-1">On-time rent collection</p>
            </div>
          </div>
        </div>
      </section>

      {/* Featured properties */}
      <section id="properties" className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-slate-900">Featured properties</h2>
          <p className="text-slate-500 mt-2">A look at what's available on SmartRent</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {FEATURED_PROPERTIES.map((property) => (
            <div
              key={property.id}
              className="bg-white rounded-2xl border border-slate-200 overflow-hidden hover:shadow-md transition-shadow"
            >
              <div className="h-44 bg-slate-200" />
              <div className="p-5">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-slate-900">{property.name}</h3>
                    <p className="text-sm text-slate-500">{property.location}</p>
                  </div>
                  <span className="bg-amber-50 text-amber-700 text-xs font-medium px-2 py-1 rounded-full">
                    {property.type}
                  </span>
                </div>

                <div className="flex items-center gap-4 text-sm text-slate-500 mt-4">
                  <span>{property.beds} bed</span>
                  <span>{property.baths} bath</span>
                </div>

                <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-100">
                  <p className="text-lg font-bold text-amber-600">
                    KES {property.price}<span className="text-sm font-normal text-slate-500">/mo</span>
                  </p>
                  <button className="text-sm font-medium text-slate-900 hover:text-amber-600">
                    View details →
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="bg-white border-y border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-900">How SmartRent works</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 rounded-full bg-amber-50 text-amber-700 flex items-center justify-center mx-auto font-semibold">1</div>
              <h3 className="font-semibold text-slate-900 mt-4">Create an account</h3>
              <p className="text-sm text-slate-500 mt-2">Sign up as a landlord or tenant in under a minute.</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 rounded-full bg-amber-50 text-amber-700 flex items-center justify-center mx-auto font-semibold">2</div>
              <h3 className="font-semibold text-slate-900 mt-4">List or lease a unit</h3>
              <p className="text-sm text-slate-500 mt-2">Landlords list properties, tenants get matched to units.</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 rounded-full bg-amber-50 text-amber-700 flex items-center justify-center mx-auto font-semibold">3</div>
              <h3 className="font-semibold text-slate-900 mt-4">Pay and manage rent</h3>
              <p className="text-sm text-slate-500 mt-2">Pay rent via M-Pesa and track everything in one dashboard.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900">
        <div className="max-w-7xl mx-auto px-6 py-12 flex flex-col md:flex-row items-center justify-between gap-4">
          <span className="text-white font-bold">SmartRent</span>
          <p className="text-sm text-slate-500">© 2026 SmartRent. Built for landlords and tenants in Kenya.</p>
        </div>
      </footer>
    </div>
  )
}

export default Landing