import RPi.GPIO as GPIO
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# GPIO setup for servo
SERVO_PIN = 17  # GPIO17 (Physical Pin 11)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Create PWM instance with 50Hz frequency (standard for servos)
pwm = None  # Initialize as None, we'll create it only when needed

# Current state tracking
current_state = "locked"

def init_pwm():
    """Initialize PWM if not already initialized"""
    global pwm
    if pwm is None:
        pwm = GPIO.PWM(SERVO_PIN, 50)
        pwm.start(0)

def cleanup_pwm():
    """Stop PWM and cleanup"""
    global pwm
    if pwm is not None:
        pwm.stop()
        pwm = None

def set_angle(angle):
    """Convert angle to duty cycle and move servo"""
    try:
        init_pwm()  # Start PWM
        duty = angle / 18 + 2  # Convert angle to duty cycle (0-180 degrees -> 2-12% duty cycle)
        logger.info(f"Setting servo to angle {angle}° (duty cycle: {duty}%)")
        pwm.ChangeDutyCycle(duty)
        time.sleep(0.5)  # Give servo time to reach position
        cleanup_pwm()  # Stop PWM after movement
        return True
    except Exception as e:
        logger.error(f"Error setting servo angle: {e}")
        cleanup_pwm()  # Ensure PWM is cleaned up even on error
        return False

app = Flask(__name__)
CORS(app)

@app.route('/control', methods=['POST'])
def control_lock():
    global current_state
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
            
        command = data.get('command', '').lower()
        logger.info(f"Received command: {command}")
        
        if command not in ['lock', 'unlock']:
            return jsonify({'error': 'Invalid command'}), 400
            
        # For unlock command, move servo to 90 degrees
        if command == 'unlock' and current_state == 'locked':
            if set_angle(90):  # Move to unlocked position
                current_state = 'unlocked'
                logger.info("Successfully unlocked")
                return jsonify({'status': 'Success', 'action': 'unlocked'})
            else:
                logger.error("Failed to move servo")
                return jsonify({'error': 'Failed to move servo'}), 500
                
        # For lock command, move servo to 0 degrees
        elif command == 'lock' and current_state == 'unlocked':
            if set_angle(0):  # Move to locked position
                current_state = 'locked'
                logger.info("Successfully locked")
                return jsonify({'status': 'Success', 'action': 'locked'})
            else:
                logger.error("Failed to move servo")
                return jsonify({'error': 'Failed to move servo'}), 500
        
        logger.info(f"No action needed, current state: {current_state}")
        return jsonify({'status': 'No action needed', 'current_state': current_state})
            
    except Exception as e:
        logger.error(f"Error: {e}")
        cleanup_pwm()  # Ensure PWM is cleaned up on error
        return jsonify({'error': str(e)}), 500

def cleanup():
    """Clean up GPIO on program exit"""
    try:
        cleanup_pwm()
        GPIO.cleanup()
    except:
        pass

if __name__ == '__main__':
    try:
        logger.info("Starting servo controller...")
        # Initialize to locked position
        if set_angle(0):
            logger.info("Initialized to locked position")
        else:
            logger.error("Failed to initialize servo position")
        
        # Run Flask app on port 5001
        logger.info("Starting Flask server on port 5001...")
        app.run(host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        cleanup()
    except Exception as e:
        logger.error(f"Error: {e}")
        cleanup()
