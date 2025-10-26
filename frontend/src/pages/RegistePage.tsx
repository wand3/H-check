import HBody from "../components/Body";
import React, { useEffect } from "react";
import { useNavigate } from 'react-router-dom';
import useFlash from "../hooks/UseFlash";
import Config from "../config";
import { useDispatch, useSelector } from 'react-redux'
import type { AppDispatch, RootState } from "../store";
import { registerUser } from "../services/auth";
import SpinnerLineWave from "../components/Spinner";
// form and yup validation 
import { yupResolver } from '@hookform/resolvers/yup';
import { useForm } from 'react-hook-form'
import { schema , type RegisterUserInputSchema } from '../schemas/auth'
import axios from "axios";



const RegisterPage = () => {

  const { loading, error, success } = useSelector((state: RootState) => state.auth); // Type-safe selector
  const dispatch = useDispatch<AppDispatch>(); // Type-safe dispatch 

  // const { register, handleSubmit, formState: { errors }, setError, clearErrors } = useForm<RegisterUserInputSchema>({
  //   resolver: yupResolver(schema)
  //   // defaultValues: {
  //   //   email: '',
  //   //   username: '',
  //   //   password: '',
  //   //   confirm: '',
  //   // }
  // });

  const {
      register,
      handleSubmit,
      formState: { errors },  setError, clearErrors
    } = useForm<RegisterUserInputSchema>({ resolver: yupResolver(schema) });
  


  const flash = useFlash();
  const navigate = useNavigate();

 
  // Redirect to login page if registration is successful
  useEffect(() => {
    // setFormerrors({})
    if (success) {
      navigate('/login'); // Replace '/login' with the actual path to your login page
      flash('Registeration successful', 'success')

    }
    flash('Failed', 'error')

  }, [success, navigate]);


  const onSubmit = async (data: RegisterUserInputSchema) => {
      try {
        console.log('onsubmit in')
        clearErrors(); // Clear any previous errors
        console.log('onsubmit clear errors')
        // check if username exist 
        const existingUserResponse = await axios.get(`${Config.baseURL}/auth/check-username?username=${data.username}`);
        // console.log(existingUserResponse)
        if (existingUserResponse.data.exists) {
          setError("username", { type: "manual", message: "Username already exists" });
          return;
        }
        // check if email exist 
        const existingUserEmailResponse = await axios.get(`${Config.baseURL}/auth/check-email?email=${data.email}`);
        // console.log(existingUserEmailResponse)
        if (existingUserEmailResponse.data.exists) {
          setError("email", { type: "manual", message: "Email already exists" });
          return;
        }

        dispatch(registerUser({
          username: data.username, email: data.email, password: data.password,
          confirm: ""
        }));
      } catch (err: any) {
        console.error("Registration error:", err);
        if (axios.isAxiosError(err)) {
          setError("root", { type: "manual", message: err.response?.data?.message || err.message || 'Registration failed due to network error' });
        } else {
          setError("root", { type: "manual", message: "An unexpected error occurred during registration." });
        }
      }
    };
 

  return (
    <>
      <HBody nav={false}>
        <section className="bg-white/70 rounded-md drop-shadow-2xl justify-around m-auto flex mt-[10%]">
          <div className="lg:grid lg:min-h-screen lg:grid-cols-12">
            <aside className="relative block h-16 lg:order-last lg:col-span-5 lg:h-full xl:col-span-6">
              <img src="/pexels-gabby-k-9430875.jpg" className="absolute inset-0 h-full w-full object-cover"/>
            </aside>

            <main
              className="flex items-center justify-center px-8 py-8 sm:px-12 lg:col-span-7 lg:px-16 lg:py-12 xl:col-span-6"
            >
              <div className="max-w-xl lg:max-w-3xl">

                <div className="max-w-xl lg:max-w-3xl shadow-lg pb-5 px-3 rounded-md">
                  <a className="block text-[#ba2a25]" href="/">
                    <span className="sr-only">Home</span>
                    {/* <StoreIcon className="h-[4rem] w-fit"/> */}
                  </a>

                  <h1 className="mt-6 text-2xl font-bold text-gray-900 sm:text-3xl md:text-4xl">
                    Welcome to H-Check<span className="inline-flex absolute mt-1 ml-1">
                    {/* <ShoppingBag /> */}
                    </span>
                  </h1>

                  <form onSubmit={handleSubmit(onSubmit)} className="mt-8 grid grid-cols-6 gap-6">
                    {/* {error && <p className="text-xs text-red-600 block">{error}</p>} */}

                    <div className="col-span-6 sm:col-span-3">
                      <label  htmlFor="Email" className="flex text-sm font-medium text-gray-700" >Email</label>
                      <input className="mt-1 w-full p-1 rounded-md border-gray-200 bg-white text-sm text-gray-700 shadow-sm" {...register("email")} />
                      {errors.email && <p className="flex mt-2 text-xs text-red-600">{errors.email.message}</p>}
                    </div>
                    
                    <div className="col-span-6 sm:col-span-3">
                      <label  htmlFor="Username" className="flex text-sm font-medium text-gray-700" >Username</label>
                      <input className="mt-1 w-full p-1 rounded-md border-gray-200 bg-white text-sm text-gray-700 shadow-sm" {...register("username")} />
                      {errors.username && <p className="flex mt-2 text-xs text-red-600">{errors.username.message}</p>}
                    </div>  

                    <div className="col-span-6 sm:col-span-3">
                      <label  htmlFor="Password" className="flex text-sm font-medium text-gray-700" >Password</label>
                      <input className="mt-1 w-full p-1 rounded-lg border-gray-200 bg-white text-sm text-gray-700 shadow-sm" type="password" {...register("password")} />
                      {errors.password && <p className="flex mt-2 text-xs text-red-600">{errors.password.message}</p>}
                    </div>  
                    
                    <div className="col-span-6 sm:col-span-3">
                      <label  htmlFor="Confirm Password" className="flex text-sm font-medium text-gray-700" >Confirm Password</label>
                      <input className="mt-1 w-full p-1 rounded-md border-gray-200 bg-white text-sm text-gray-700 shadow-sm" type="password" {...register("confirm")} />
                      {errors.confirm && <p className="flex mt-2 text-xs text-red-600">{errors.confirm.message}</p>}
                    </div>   

                    <div className="col-span-6 py-2">
                      <label htmlFor="MarketingAccept" className="flex gap-4">
                        <input
                          type="checkbox"
                          id="MarketingAccept"
                          name="marketing_accept"
                          className="size-5 rounded-md border-gray-200 bg-white shadow-sm"
                        />
                        <span className="text-sm text-gray-700">
                          I want to receive emails about events, product updates and company announcements.
                        </span>
                      </label>
                    </div>

                    <div className="col-span-6 py-2">
                      <p className="text-sm text-gray-500">
                        By creating an account, you agree to our
                        <a href="#" className="text-gray-700 underline"> terms and conditions </a>
                      </p>
                    </div>

                    <div className="col-span-6 sm:flex sm:items-center sm:gap-4">
                      <button
                        className="inline-block shrink-0 rounded-md border border-blue-600 bg-blue-600 px-10 py-3 text-sm font-medium text-white transition hover:bg-transparent hover:text-blue-600 focus:outline-none focus:ring active:text-blue-500"
                        type="submit" aria-disabled={loading}
                      >
                        {loading ? <SpinnerLineWave /> : 'Create Account'}
                      </button>

                      <p className="mt-4 text-sm text-gray-500 sm:mt-0">
                        Already have an account?
                        <a href="/login" className="text-gray-700 underline">Log in</a>.
                      </p>
                    </div>
                      
                  </form>


                </div>
              </div>
            </main>
          </div>
        </section> 
      </HBody>        
    </>
  );
};

export default RegisterPage;