import { BrowserRouter as Router, Routes, Route, useNavigate } from "react-router-dom";
import { RegisterScreen } from "./screens/Register";
import { LoginScreen } from "./screens/Login";
import { ControlScreen } from "./screens/Control";
import { StyledButton } from "./components/StyledButton";
import "./App.css";

function NavBar() {
  const navigate = useNavigate();

  return (
    <div className="width-full h-22 bg-[#fffedf] rounded-b-2xl display flex justify-between items-center px-4 py-2 text-3xl text-[#ff782a]">
      <div 
        className="font-bold hover:cursor-pointer"
        onClick={() => navigate('/')}
      >
        HOUSELINK
      </div>
      <StyledButton
        text="Login"
        onClick={() => navigate('/login')}
        size="3xl"
      />
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="App h-screen flex flex-col bg-gradient-to-br from-[#ff782a] to-[#ffd6a7]">
        <NavBar />
        <div className="flex-1 flex justify-center overflow-hidden w-full">
          <div className="w-[40%] max-h-[80%] bg-[#fffedf] mt-20 text-3xl rounded-4xl">
            <Routes>
              <Route path="/" element={<RegisterScreen />} />
              <Route path="/register" element={<RegisterScreen />} />
              <Route path="/login" element={<LoginScreen />} />
              <Route path="/control" element={<ControlScreen />} />
            </Routes>
          </div>
        </div>
      </div>
    </Router>
  );
}

export default App;
