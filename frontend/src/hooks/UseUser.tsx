import UserContext from "../context/UserProvider";
import { useContext } from "react";
import { UserContextType } from "../context/UserProvider";

export function useUser() {
    return useContext(UserContext) as UserContextType;
}

export default useUser;