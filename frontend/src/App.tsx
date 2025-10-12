import './App.css';
import { Routes, Route } from "react-router-dom";
import Home from './pages/Home';
import { FlashProvider } from './context/FlashProvider';



function App() {

  return (
    <>
      <FlashProvider>
          <Routes>
             <Route path="/home" element={ <Home />} />
          </Routes>
      </FlashProvider>
    </>
  )
}

export default App