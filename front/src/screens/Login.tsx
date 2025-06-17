import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { StyledInput } from "../components/StyledInput";
import { StyledButton } from "../components/StyledButton";

export function LoginScreen() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    try {
      setMessage(null);
      setLoading(true);

      console.log('Attempting login with:', { email });

      const response = await fetch('http://localhost:5000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          username: email, 
          password 
        }),
      });

      const data = await response.json();
      console.log('Login response:', data);

      if (response.ok) {
        setMessage('Login successful!');
        // Navigate to control page after successful login
        navigate('/control');
      } else {
        setMessage(data.message || 'Login failed');
      }
    } catch (err) {
      console.error('Login error:', err);
      setMessage('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <h1 className="ml-5 mt-5 font-semibold">LOGIN</h1>
      <div className="flex flex-col w-full px-10 mt-5 gap-3">
        <h2 className="mt-15">Email:</h2>
        <StyledInput
          text="Email"
          size="lg"
          placeholder="Ex: myemail@email.com"
          margin="mb-15"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <h2>Password:</h2>
        <StyledInput
          text="Password"
          size="lg"
          placeholder="Enter your password"
          type="password"
          margin="mb-25"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <StyledButton
          text={loading ? "Logging in..." : "GET STARTED"}
          onClick={handleLogin}
          size="2xl"
          hover="hover:bg-[#d6570d]"
        />
        {message && (
          <div className={`text-sm mt-2 ${message.includes('successful') ? 'text-green-600' : 'text-red-500'}`}>
            {message}
          </div>
        )}
        <p className="text-sm text-center mt-2">
          Don't have an account?{" "}
          <span 
            className="text-[#ff782a] cursor-pointer hover:text-[#d6570d]"
            onClick={() => navigate('/register')}
          >
            Register here
          </span>
        </p>
      </div>
    </>
  );
}
