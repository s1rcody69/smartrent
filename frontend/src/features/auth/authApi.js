import { apiSlice } from '../../app/api'

export const authApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({

    register: builder.mutation({
      query: (userData) => ({
        url: 'auth/register/',
        method: 'POST',
        body: userData,
      }),
    }),

    login: builder.mutation({
      query: (credentials) => ({
        url: 'auth/login/',
        method: 'POST',
        body: credentials,
      }),
    }),

    logout: builder.mutation({
      query: (refreshToken) => ({
        url: 'auth/logout/',
        method: 'POST',
        body: { refresh: refreshToken },
      }),
    }),

    getCurrentUser: builder.query({
      query: () => 'auth/me/',
      providesTags: ['User'],
    }),

    refreshAccessToken: builder.mutation({
      query: (refreshToken) => ({
        url: 'auth/token/refresh/',
        method: 'POST',
        body: { refresh: refreshToken },
      }),
    }),

  }),
})

// RTK Query auto-generates these hooks from the endpoint names above
export const {
  useRegisterMutation,
  useLoginMutation,
  useLogoutMutation,
  useGetCurrentUserQuery,
  useRefreshAccessTokenMutation,
} = authApi