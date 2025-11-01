import Config from '../config';
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { RootState } from '../store'; // Import your RootState type
import type { UserInDBSchema } from '../schemas/user';

export const authApi = createApi({
  reducerPath: 'authApi',
  baseQuery: fetchBaseQuery({
    baseUrl: Config.baseURL,
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token; // Type the getState result
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      return headers; // Important: Return the headers
    },
  }),
  endpoints: (builder) => ({
    getUserDetails: builder.query<UserInDBSchema, void>({ // Type the query result and argument
      query: () => ({
        url: `${Config.baseURL}/user/me`,
        method: 'GET',
      }),
    }),

    // Mutation: To log out the user
    logout: builder.mutation<void, void>({ // <ResultType, ArgType>
      // Clear stored tokens or session data
      // localStorage.removeItem('authToken'),
      // sessionStorage.clear(),
      query: () => ({
        url: `/auth/logout`, 
        method: 'POST', // Use POST or DELETE for state-changing operations
      }),
      // Optional: Logic to clear state/cache can be added here or in an onQueryStarted
    }),
  }),
});

export const { useGetUserDetailsQuery, useLogoutMutation } = authApi; // Export the hook