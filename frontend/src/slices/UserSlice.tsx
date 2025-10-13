import { UserInDBSchema } from '../schemas/user';
import { createSlice, PayloadAction } from '@reduxjs/toolkit'

// initialize userToken from local storage
const storedToken = localStorage.getItem('token');
const initialToken = storedToken || null;


export interface UserState {
  loading: boolean;
  user: UserInDBSchema | null;
  error: string | null;
  token: string | null;
  success: boolean;
}

const initialState : UserState = {
  loading: false,
  user: null,
  error: null,
  success: false,
  token: initialToken,
}


const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers : {
    logout: (state) => {
      state.user = null;
      state.token = null;
      localStorage.removeItem('token'); // Remove token from local storage
    },
    setCredentials: (state, action: PayloadAction<UserInDBSchema>) => {
      state.user = action.payload;
    },
  },

  extraReducers: (builder) => {
    builder
  },

})

export const { logout, setCredentials } = userSlice.actions
export default userSlice.reducer
