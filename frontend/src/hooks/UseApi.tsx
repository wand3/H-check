import { useContext } from "react";
// import ApiProvider from "../context/ApiProvider";
import ApiClient from "../ApiClient";
import { ApiContext } from "../context/ApiProvider";

export const UseApi = () => {
    return useContext(ApiContext) as ApiClient;

}

export default UseApi;