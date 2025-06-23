import { useState } from "react";
import { StyledButton } from "../components/StyledButton";

export function ControlScreen() {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const RASPBERRY_PI_URL = 'http://192.168.198.84:5001/control';

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
      <h1 className="ml-5 mt-5 font-semibold flex flex-col">CONTROL</h1>
      <div className="flex flex-col w-full px-10 mt-30 gap-20">
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
          <div className="flex justify-center mt-4">
            <div
              className={`text-lg font-semibold transition-transform transform duration-500 ease-in-out ${
                message.includes("Successfully")
                  ? "text-green-600 scale-110"
                  : "text-red-500 scale-90"
              }`}
            >
              {message}
            </div>
          </div>
        )}
      </div>
    </>
  );
}