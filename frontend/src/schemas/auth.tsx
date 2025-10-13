import * as yup from "yup";
import { UserSchema } from "./user";


// register 
export interface RegisterUserInputSchema {
  username: string;
  email: string;
  password: string;
  confirm: string;
}

export interface RegisterUserOutputSchema {
  email: string
  username: string
  disabled?: boolean
  profile_pic?: string
}


// login 
export interface LoginUserInputSchema {
  username: string;
  password: string;
}

export interface LoginUserOutputSchema {
  user: UserSchema;
  access_token: string;
}


export const schema = yup.object().shape({
  email: yup.string().email("Invalid email").required("Email is required"),
  username: yup
    .string()
    .matches(/^[a-zA-Z0-9_!\-.]+$/, "Username can only contain letters, numbers, _, -, !, and .")
    .required("Username is required"),
  password: yup.string().min(6, "Password must be at least 6 characters").required("Password is required"),
  confirm: yup
    .string()
    .oneOf([yup.ref('password')], "Passwords must match")
    .required("Confirm password is required"),
});

export const schemaLogin = yup.object().shape({
  username: yup
    .string()
    .matches(/^[a-zA-Z0-9_!\-.]+$/, "Username can only contain letters, numbers, _, -, !, and .")
    .required("Username is required"),
  password: yup.string().min(6, "Password must be at least 6 characters").required("Password is required")
});