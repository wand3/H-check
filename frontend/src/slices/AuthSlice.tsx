import type { UserSchema } from '../schemas/user';
import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit';

import { registerUser, loginUser } from '../services/auth';


// initialize userToken from local storage
export const userToken = localStorage.getItem('token')
  ? localStorage.getItem('token')
  : null



interface AuthState {
  loading: boolean;
  user: UserSchema | null; // Store user object or null
  token: string | null; // Store JWT or null
  error: string | null; // Store error message or null
  success: boolean; // Monitor registration or other operations
}

const initialState: AuthState = {
  user: null,
  token: userToken,
  loading: false,
  error: null,
  success: false,
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      state.user = null;
      state.token = null;
      localStorage.removeItem('token'); // Remove token from local storage
    },
  },
  extraReducers: (builder) => {
    builder
    // -------------- user login 
    // loginUser pending 
    .addCase(loginUser.pending, (state) => {
      state.loading = true;
      state.error = null;
    })
    // loginUser.fulfilled 
    .addCase(loginUser.fulfilled, (state, action: PayloadAction<{user: UserSchema; access_token: string}>) => { // Type the payload
        state.loading = false;
        state.user = action.payload.user;
        console.log(state.user)
        state.success = true;
        state.token = action.payload.access_token;
      })


    // loginUser.rejected
    .addCase(loginUser.rejected, (state, action: PayloadAction<string | undefined>) => {
      state.loading = false;
      state.error = action.payload || 'Login failed';
    })



    // -------------- user registeration 
    // registerUser.pending 
    .addCase(registerUser.pending, (state) => {
      state.loading = true;
      state.error = null;
    })
    // registerUser.fulfilled || success 
    .addCase(registerUser.fulfilled, (state) => {
      state.loading = false;
      state.success = true;
    })
    // registerUser.rejected 
    .addCase(registerUser.rejected, (state, action: PayloadAction<string | undefined>) => {
      state.loading = false;
      state.error = action.payload || 'Registeration failed';
    })
  
  },

})

export const { logout } = authSlice.actions;

export default authSlice.reducer
