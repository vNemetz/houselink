import { useState } from "react";
import { StyledButton } from "../components/StyledButton";

export function ControlScreen() {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const RASPBERRY_PI_URL = 'http://192.168.18.87:5001/control';

  const sendCommand = async (command: 'lock' | 'unlock') => {
    try {
      setLoading(true);
      setMessage(null);

      const response = await fetch(RASPBERRY_PI_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command }),
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessage(`Successfully ${command}ed!`);
      } else {
        setMessage(data.error || 'Failed to send command');
      }
    } catch (err) {
      console.error(`Error sending ${command} command:`, err);
      setMessage('Failed to connect to the device');
    } finally {
      setLoading(false);
    }
  };

  const handleOpen = () => {
    sendCommand('unlock');
  };

  const handleClose = () => {
    sendCommand('lock');
  };

  return (
    <>
      <h1 className="ml-5 mt-5 font-semibold">CONTROL</h1>
      <div className="flex flex-col w-full px-10 mt-5 gap-6">
        <StyledButton
          text={loading ? "PROCESSING..." : "OPEN"}
          onClick={handleOpen}
          size="2xl"
          hover="hover:bg-[#d6570d]"
        />
        <StyledButton
          text={loading ? "PROCESSING..." : "CLOSE"}
          onClick={handleClose}
          size="2xl"
          hover="hover:bg-[#d6570d]"
        />
        {message && (
          <div 
            className={`text-center mt-4 ${
              message.includes('Successfully') ? 'text-green-600' : 'text-red-500'
            }`}
          >
            {message}
          </div>
        )}
      </div>
    </>
  );
}