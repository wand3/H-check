import { LineWave } from "react-loader-spinner";

export const SpinnerLineWave = () => {
   

    return (
        <LineWave
            visible={true}
            height="60"
            width="60"
            color="#4fa94d"
            ariaLabel="line-wave-loading"
            wrapperStyle={{}}
            wrapperClass=""
            firstLineColor="#000000"
            middleLineColor=""
            lastLineColor=""
        />
    );
          
}

export default SpinnerLineWave;