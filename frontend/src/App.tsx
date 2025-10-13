import './App.css';
import { Routes, Route } from "react-router-dom";
import Home from './pages/Home';
import { FlashProvider } from './context/FlashProvider';
import ApiProvider from './context/ApiProvider';
import { UserProvider } from './context/UserProvider';


function App() {

  return (
    <>
      <FlashProvider>
        <ApiProvider>
            <UserProvider>
              <Routes>
                <Route path="/home" element={ <Home />} />
              </Routes>
            </UserProvider>
        </ApiProvider>
      </FlashProvider>
    </>
  )
}

export default App