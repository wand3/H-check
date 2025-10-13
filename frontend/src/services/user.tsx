import Config from '../config';
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { RootState } from '../store'; // Import your RootState type
import { UserInDBSchema } from '../schemas/user';

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
  }),
});

export const { useGetUserDetailsQuery } = authApi; // Export the hook