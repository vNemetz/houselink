import RPi.GPIO as GPIO
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# GPIO setup for DC motor with L298N
PWM_PIN = 18  # GPIO18 (Physical Pin 12)
IN1_PIN = 23  # GPIO23 (Physical Pin 16)
IN2_PIN = 24  # GPIO24 (Physical Pin 18)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.setup(IN1_PIN, GPIO.OUT)
GPIO.setup(IN2_PIN, GPIO.OUT)

# Create PWM instance for speed control
pwm = GPIO.PWM(PWM_PIN, 100)  # 100Hz frequency
pwm.start(0)  # Start with 0% duty cycle

# Current state tracking
current_state = "locked"

# Ensure the motor is always running at 100% power

def set_motor(direction: str, speed: int = 100):
    """Control motor direction and ensure full power"""
    try:
        if direction == "forward":
            GPIO.output(IN1_PIN, GPIO.HIGH)
            GPIO.output(IN2_PIN, GPIO.LOW)
        elif direction == "backward":
            GPIO.output(IN1_PIN, GPIO.LOW)
            GPIO.output(IN2_PIN, GPIO.HIGH)
        else:
            GPIO.output(IN1_PIN, GPIO.LOW)
            GPIO.output(IN2_PIN, GPIO.LOW)

        pwm.ChangeDutyCycle(100)  # Always set to 100% duty cycle
        logger.info(f"Motor set to {direction} with full power (100%)")
        return True
    except Exception as e:
        logger.error(f"Error controlling motor: {e}")
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
            
        # For unlock command, move motor forward
        if command == 'unlock' and current_state == 'locked':
            if set_motor("forward", 100):  # Full speed forward
                time.sleep(3)  # Run motor for 2 seconds
                set_motor("stop", 0)  # Stop motor
                current_state = 'unlocked'
                logger.info("Successfully unlocked")
                return jsonify({'status': 'Success', 'action': 'unlocked'})
            else:
                logger.error("Failed to control motor")
                return jsonify({'error': 'Failed to control motor'}), 500
                
        # For lock command, move motor backward
        elif command == 'lock' and current_state == 'unlocked':
            if set_motor("backward", 100):  # Full speed backward
                time.sleep(3)  # Run motor for 2 seconds
                set_motor("stop", 0)  # Stop motor
                current_state = 'locked'
                logger.info("Successfully locked")
                return jsonify({'status': 'Success', 'action': 'locked'})
            else:
                logger.error("Failed to control motor")
                return jsonify({'error': 'Failed to control motor'}), 500
        
        logger.info(f"No action needed, current state: {current_state}")
        return jsonify({'status': 'No action needed', 'current_state': current_state})
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/state', methods=['GET'])
def get_motor_state():
    """Endpoint to retrieve the current state of the motor."""
    try:
        logger.info(f"Current motor state: {current_state}")
        return jsonify({'current_state': current_state})
    except Exception as e:
        logger.error(f"Error retrieving motor state: {e}")
        return jsonify({'error': str(e)}), 500

def cleanup():
    """Clean up GPIO on program exit"""
    try:
        pwm.stop()
        GPIO.cleanup()
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

if __name__ == '__main__':
    try:
        logger.info("Starting DC motor controller...")
        # Initialize motor to stopped state
        set_motor("stop", 0)
        
        # Run Flask app on port 5001
        logger.info("Starting Flask server on port 5001...")
        app.run(host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        cleanup()
    except Exception as e:
        logger.error(f"Error: {e}")
        cleanup()
