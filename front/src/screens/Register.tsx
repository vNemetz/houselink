import { useState } from "react";
import { StyledInput } from "../components/StyledInput";
import { StyledButton } from "../components/StyledButton";

export function RegisterScreen() {
  const [serial, setSerial] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    try {
      setMessage(null);

      if (password !== confirmPassword) {
        setMessage("Passwords do not match");
        return;
      }

      setLoading(true);
      console.log("Attempting registration with:", { email });

      const response = await fetch("http://localhost:5000/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: email,
          password,
          serial, // Adding serial number if backend needs it
        }),
      });

      const data = await response.json();
      console.log("Registration response:", data);

      if (response.ok) {
        setMessage("Registration successful! You can now log in.");
      } else {
        setMessage(data.message || "Registration failed");
      }
    } catch (err) {
      console.error("Registration error:", err);
      setMessage("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

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
          value={serial}
          onChange={(e) => setSerial(e.target.value)}
        />
        <h2>Email:</h2>
        <StyledInput
          text="Email"
          size="lg"
          placeholder="Enter your email (registered when you bought the device)"
          margin="mb-3"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <h2>New Password:</h2>
        <StyledInput
          text="Password"
          size="lg"
          placeholder="Enter your password"
          type="password"
          margin="mb-3"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <h2>Confirm Password:</h2>
        <StyledInput
          text="Confirm Password"
          size="lg"
          placeholder="Confirm your password (retype it)"
          type="password"
          margin="mb-6"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
        />
        <StyledButton
          text={loading ? "Registering..." : "SUBMIT"}
          onClick={handleRegister}
          size="2xl"
          hover="hover:bg-[#d6570d]"
        />
        {message && (
          <div
            className={`text-sm mt-2 ${
              message.includes("successful")
                ? "text-green-600"
                : "text-red-500"
            }`}
          >
            {message}
          </div>
        )}
      </div>
    </>
  );
}
