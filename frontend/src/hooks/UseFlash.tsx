import FlashContext from "../context/FlashProvider";
import { useContext } from "react";
import { FlashContextType } from "../context/FlashProvider";

export const useFlash = () => {
    return (useContext(FlashContext) as FlashContextType).flash;

}

export default useFlash;