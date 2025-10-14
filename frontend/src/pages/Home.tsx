import HBody from "../components/Body";

const Home = () => {

    return (
        <> 
            <HBody nav={false}>
              <h1 className='text-lg text-center text-white'>Homepage success</h1>
              <div id="chat-container">
                    <div id="messages"></div>
                    <form id="message-form">
                    <input type="text" id="message-input" placeholder="Type your message" autocomplete="off" />
                    <button type="submit">Send</button>
                    </form>
                </div>
            </HBody>
        </>
    )
}

export default Home;