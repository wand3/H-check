
export interface UserSchema {
  username?: string;
  email?: string;
  disabled: string;
  profile_pic?: string;
}


export interface UserInDBSchema {
  id: string;
  username: string;
  email: string;
  disabled: string;
  profile_pic?: string;
  created_at: string;
  updated_at: string;
}
