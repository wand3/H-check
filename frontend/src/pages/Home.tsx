import HBody from "../components/Body";
import FhirBot from "../components/ChatBot";

const Home = () => {

    return (
        <> 
            <HBody nav={false}>
              <FhirBot />
              
            </HBody>
        </>
    )
}

export default Home;