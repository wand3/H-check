import HBody from "../components/Body";
import React, { useEffect } from "react";
import { useNavigate } from 'react-router-dom';
import useFlash from "../hooks/UseFlash";
import Config from "../config";
import { useDispatch, useSelector } from 'react-redux'
import type { AppDispatch, RootState } from "../store";
import { loginUser } from "../services/auth";
import SpinnerLineWave from "../components/Spinner";
// form and yup validation 
import { yupResolver } from '@hookform/resolvers/yup';
import { useForm } from 'react-hook-form'
import { schemaLogin , type LoginUserInputSchema } from '../schemas/auth'
import axios from "axios";


const LoginPage = () => {
  const { loading, error, success } = useSelector((state: RootState) => state.auth)
  const dispatch = useDispatch<AppDispatch>(); // Type-safe dispatch 
  const {
    register,
    handleSubmit,
    formState: { errors }, setError, clearErrors
  } = useForm<LoginUserInputSchema>({ resolver: yupResolver(schemaLogin)})
 
  const flash = useFlash();
  const navigate = useNavigate();
  

  // Redirect to home page if registration is successful
  useEffect(() => {
    // setFormerrors({})

    if (success) {
      navigate('/home'); // Replace '/login' with the actual path to your login page
      flash('Welcome to FHIR Assistant', 'success')

    }
    if (error) {
      flash('Failed', 'error')
    }

  }, [success, navigate]);

  const onSubmit = async (data: LoginUserInputSchema) => {
    try {
        console.log('onsubmit in')
        clearErrors(); // Clear any previous errors
        console.log('onsubmit clear errors')
        // check if username exist 
        

        const j = dispatch(loginUser({
          username: data.username, password: data.password,
        }));
        console.log('post dispatch clear errors')
        console.log(j)

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
        <section className="bg-white/70 rounded-md drop-shadow-2xl relative z-10 mt-[-4.75rem] justify-around m-auto flex mt-[10%]">
          <div className="lg:grid lg:min-h-screen lg:grid-cols-12">
            <section className="relative flex h-32 items-end lg:col-span-5 lg:h-full xl:col-span-6">
              <img
                alt="login-banner"
                src="/pexels-gabby-k-9430875.jpg"
                className="absolute inset-0 h-full w-full object-cover opacity-80"
              />
              <div className="hidden lg:relative lg:block lg:p-12">

                <a className="block text-[#ba2a25] p-2" href="/">
                  <span className="sr-only">Home</span>
                  {/* <StoreIcon className="h-[4rem] w-fit"/> */}

                </a>

                <h2 className="mt-6 text-2xl font-bold text-white sm:text-3xl md:text-4xl">
                </h2>
              </div>
            </section>

            <main
              className="flex items-center justify-center px-8 py-8 sm:px-12 lg:col-span-7 lg:px-16 lg:py-12 xl:col-span-6"
            >
              <div className="max-w-xl lg:max-w-3xl shadow-lg pb-5 px-3 rounded-md">
                <div className="relative -mt-16 block lg:hidden">
                  <a
                    className="inline-flex size-16 text-[#ba2a25] p-2 items-center justify-center rounded-full bg-white sm:size-20"
                    href="/"
                  >
                    <span className="sr-only">Home</span>
                    {/* <StoreIcon className="h-[4rem] w-fit"/> */}

                  </a>

                  <h1 className="mt-2 text-2xl font-bold text-gray-900 sm:text-3xl md:text-4xl">
                    {/* Welcome to KASUWA<span className="inline-flex absolute mt-1 ml-1"><ShoppingBag /></span> */}
                  </h1>

                  <p className="mt-4 leading-relaxed text-gray-500">
                    H-Check, your AI-powered healthcare data querying tool that interfaces with FHIR-compliant systems
                  </p>
                </div>

                <form onSubmit={handleSubmit(onSubmit)} className="mt-8 grid grid-cols-6 gap-6">
                    {error && <p className="text-xs text-red-600 block">{error}</p>}
                    
                    <div className="col-span-6 sm:col-span-3">
                      <label  htmlFor="Username" className="flex text-sm font-medium text-gray-700" >Username</label>
                      <input className="mt-1 p-1 w-full rounded-md border-gray-200 bg-white text-sm text-gray-700 shadow-sm" {...register("username")} />
                      {errors.username && <p className="flex mt-2 text-xs text-red-600">{errors.username.message}</p>}
                    </div>  

                    <div className="col-span-6 sm:col-span-3">
                      <label  htmlFor="Password" className="flex text-sm font-medium text-gray-700" >Password</label>
                      <input className="mt-1 p-1 w-full rounded-lg border-gray-200 bg-white text-sm text-gray-700 shadow-sm" type="password" {...register("password")} />
                      {errors.password && <p className="flex mt-2 text-xs text-red-600">{errors.password.message}</p>}
                    </div>  

                  <div className="col-span-6">
                    <label htmlFor="SignInAccept" className="flex gap-4">
                      <input
                        type="checkbox"
                        id="SignInAccept"
                        name="signed_in_accept"
                        className="size-4 rounded-md border-gray-200 bg-white shadow-sm"
                      />

                      <span className="text-sm text-gray-700">
                        Keep account Signed in
                      </span>
                    </label>
                  </div>

                  

                  <div className="col-span-6 sm:flex sm:items-center sm:gap-4">
                      <button
                        className="inline-block shrink-0 rounded-md border border-blue-600 bg-blue-600 px-10 py-3 text-sm font-medium text-white transition hover:bg-transparent hover:text-blue-600 focus:outline-none focus:ring active:text-blue-500"
                        type="submit" aria-disabled={loading}
                      >
                        {loading ? <SpinnerLineWave /> : 'Login'}
                      </button>

                    <p className="mt-4 text-sm text-gray-500 sm:mt-0">
                      Don't have an account?
                      <a href="/register" className="text-gray-700 underline"> Sign up!</a>.
                    </p>
                  </div>
                </form>
              </div>
            </main>
          </div>
        </section>          
      </HBody>
    </>
  );
};


export default LoginPage;

