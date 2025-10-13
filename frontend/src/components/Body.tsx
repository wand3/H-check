// import NavMain from "./NavMain";
import React, { FC } from "react";
import FlashMessage from "./FlashMessage";



type BodyProps = {
  nav: boolean;
  children?: React.ReactNode;
};

const HBody: FC<BodyProps> = ({ nav, children }) => {
  return (
    <>
    {/* dark:bg-[#F4F2F0] */}
      {/* <div className="inset-0 radial-blur top-[-15%] sm:top-[-10%] h-[115vh] sm:h-[80vh] md:h-[120vh] mx-[5%] rounded-lg lg:mt-0 lg:h-[96vh] left-1/3 w-[96%] sm:w-[100vw] -translate-x-1/2 overflow-hidden fixed"></div> */}

      <div className="bg-[#e7f0c6] dark:bg-[#000000] p-5">
        {/* <div className="font-sans bg-gray-500 bg-clip-padding backdrop-filter  backdrop-blur bg-opacity-10 backdrop-saturate-100 backdrop-contrast-100"> */}

        {/* <div className="font-sans"> */}


          {children}
          <h1>Test to see</h1>
        {/* </div> */}
        
      </div>
    </>
)};

export default HBody;
