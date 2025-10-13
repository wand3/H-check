import { createAsyncThunk, isRejectedWithValue } from '@reduxjs/toolkit';
import axios, {AxiosError} from 'axios';
import { RegisterUserInputSchema, RegisterUserOutputSchema, LoginUserInputSchema, LoginUserOutputSchema } from '../schemas/auth';
import Config from '../config';



// register user thunk
export const registerUser = createAsyncThunk<RegisterUserOutputSchema, RegisterUserInputSchema, { rejectValue: string}> (
  'auth/register',
  async ({ username, email, password }: RegisterUserInputSchema, { rejectWithValue }) => { 
    try {
      const config = {
        headers: {
          'Content-Type': 'application/json',
        },
      };
      const response = await axios.post(
        `${Config.baseURL}/auth/register`,
        { username, email, password },
        config
      );
      if (response.status === 201) {
        return response.data
      }
    } catch (error) {
      // Handle Axios errors with type safety
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<{ message: string }>;
        if (axiosError.response && axiosError.response.data.message) {
          return rejectWithValue(axiosError.response.data.message);
        }
      }
      // Handle non-Axios errors or generic error messages
      return rejectWithValue((error as Error).message);
    }
  }

);


// Async thunk for login
export const loginUser = createAsyncThunk<
  LoginUserOutputSchema,
  // LoginUserInputSchema,
  {username: string, password: string}, 
  { rejectValue: string }
>('auth/login', async (credentials, { rejectWithValue }) => {
  try {
    const config = {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    };
    const formData = new FormData(); // Create FormData object
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    const response = await axios.post<LoginUserOutputSchema>(
      `${Config.baseURL}/token`,
      formData,
      // {username, password},
      config
    );
    console.log('token call')

    localStorage.setItem('token', response.data.access_token); // Store token in local storage
    console.log('token set submit clear errors')
    return response.data; // Return the entire response data
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || 'Login failed');
  }
}); 



