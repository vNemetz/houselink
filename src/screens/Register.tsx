import { StyledInput } from "../components/StyledInput";
import { StyledButton } from "../components/StyledButton";

export function RegisterScreen() {
  return (
    <>
      <h1 className="ml-5 mt-5 font-semibold">REGISTER DEVICE</h1>
      <div className="flex flex-col w-full px-10 mt-5 gap-2">
        <h2>Serial Number:</h2>
        <StyledInput
          text="Serial Number"
          size="lg"
          placeholder="Ex: 124AB3C4"
          margin="mb-3"
        />
        <h2>Email:</h2>
        <StyledInput
          text="Email"
          size="lg"
          placeholder="Enter your email (registered when you bought the device)"
          margin="mb-3"
        />
        <h2>New Password:</h2>
        <StyledInput
          text="Password"
          size="lg"
          placeholder="Enter your password"
          type="password"
          margin="mb-3"
        />
        <h2>Confirm Password:</h2>
        <StyledInput
          text="Confirm Password"
          size="lg"
          placeholder="Confirm your password (retype it)"
          type="password"
          margin="mb-6"
        />
        <StyledButton
        text="SUBMIT"
        onClick={() => {
          console.log("Submit clicked");
        }}
        size="2xl"
        hover="hover:bg-[#d6570d]"
        ></StyledButton>
      </div>

    </>
  );
}
