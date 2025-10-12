import { createContext, useCallback, useState, type JSX } from "react";

export type FlashContextType = {
    flash: (message: string | JSX.Element, type: string, duration?: number) => void;
    hideFlash: () => void;
    flashMessage: { message?: string | JSX.Element , type?: string};
    visible: boolean;
}

export const FlashContext = createContext<FlashContextType | null>(null);
let flashTimer: number | undefined;

export const FlashProvider = ({ children }: React.PropsWithChildren<{}>) => {
    const [ flashMessage, setFlashMessage ] = useState<{ message?: string | JSX.Element , type?: string}>({});
    const [ visible, setVisible ] = useState(false);

    const hideFlash = useCallback(() => {
        setVisible(false);
    }, []);

    const flash = useCallback((message: string | JSX.Element, type: string, duration = 5) => {
        if (flashTimer) {
            window.clearTimeout(flashTimer);
            flashTimer = undefined;
        }
        setFlashMessage({message, type});
        setVisible(true);
        if (duration) {
            flashTimer = window.setTimeout(hideFlash, duration * 1000);
        }
    }, [hideFlash]);


    return (
        <FlashContext.Provider value={{flash, hideFlash, flashMessage, visible}}>
            {children}
        </FlashContext.Provider>

    )
}


export default FlashContext;