import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

// Base URL points to your Django backend
// Change this to your Render URL when testing the deployed version
const BASE_URL = 'http://127.0.0.1:8000/api/'

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: BASE_URL,
    // prepareHeaders runs before every request — this is where we attach the JWT
    prepareHeaders: (headers, { getState }) => {
      const token = getState().auth.accessToken
      if (token) {
        headers.set('Authorization', `Bearer ${token}`)
      }
      return headers
    },
  }),
  // tagTypes lets different features tell each other "hey, this data changed, refetch"
  tagTypes: ['Property', 'Unit', 'Lease', 'Maintenance', 'Invoice', 'Payment', 'User'],
  endpoints: () => ({}), // each feature file injects its own endpoints into this
})