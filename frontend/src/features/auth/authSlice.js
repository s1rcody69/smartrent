import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  user: null,
  accessToken: null,
  refreshToken: null,
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    // Called right after login or register succeeds
    setCredentials: (state, action) => {
      const { user, tokens } = action.payload
      state.user = user
      state.accessToken = tokens.access
      state.refreshToken = tokens.refresh
    },
    // Called when refresh token returns a new access token
    setAccessToken: (state, action) => {
      state.accessToken = action.payload.access
    },
    // Called on logout
    clearCredentials: (state) => {
      state.user = null
      state.accessToken = null
      state.refreshToken = null
    },
  },
})

export const { setCredentials, setAccessToken, clearCredentials } = authSlice.actions
export default authSlice.reducer