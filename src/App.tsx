import { useState } from "react";
import { RegisterScreen } from "./screens/Register";
import { StyledButton } from "./components/StyledButton";
import "./App.css";

function App() {
  return (
    <>
      <div className="App h-screen flex flex-col">
        {/* navbar */}
        <div className="width-full h-22 bg-[#fffedf] rounded-b-2xl display flex justify-between items-center px-4 py-2 text-3xl text-[#ff782a]">
          <div className="font-bold hover:cursor-pointer">HOUSELINK</div>
          <StyledButton
            text="Login"
            onClick={() => {
              console.log("Login clicked");
            }}
            size="3xl"
          ></StyledButton>
        </div>
        <div className="flex-1 flex justify-center overflow-hidden w-full">
          <div className=" w-[40%] max-h-[75%] bg-[#fffedf] mt-20 text-3xl rounded-4xl font-">
            <RegisterScreen />
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
