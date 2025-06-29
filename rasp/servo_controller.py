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
REED_PIN = 17  # GPIO17 for reed switch
REED_PIN_2 = 5  # GPIO27 for second reed switch

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.setup(IN1_PIN, GPIO.OUT)
GPIO.setup(IN2_PIN, GPIO.OUT)
GPIO.setup(REED_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Setup reed switch with pull-up resistor
GPIO.setup(REED_PIN_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Setup second reed switch

# Create PWM instance for speed control
pwm = GPIO.PWM(PWM_PIN, 100)  # 100Hz frequency
pwm.start(0)  # Start with 0% duty cycle

# Current state tracking
current_state = "locked"

def check_reed_switch():
    """Check if reed switch is closed (magnet is present)"""
    return GPIO.input(REED_PIN) == 0  # Returns True when circuit is closed

def check_reed_switch_2():
    """Check if second reed switch is closed (magnet is present)"""
    return GPIO.input(REED_PIN_2) == 0  # Returns True when circuit is closed

def set_motor(direction: str, speed: int):
    """Control motor direction and speed"""
    try:
        # Removida a verificação do reed switch aqui
        if direction == "forward":
            GPIO.output(IN1_PIN, GPIO.HIGH)
            GPIO.output(IN2_PIN, GPIO.LOW)
        elif direction == "backward":
            GPIO.output(IN1_PIN, GPIO.LOW)
            GPIO.output(IN2_PIN, GPIO.HIGH)
        else:  # stop
            GPIO.output(IN1_PIN, GPIO.LOW)
            GPIO.output(IN2_PIN, GPIO.LOW)

        pwm.ChangeDutyCycle(speed)
        logger.info(f"Motor set to {direction} with speed {speed}%")
        return True
    except Exception as e:
        logger.error(f"Error controlling motor: {e}")
        return False

def motor_action(direction: str, duration: int):
    """Run motor with reed switch monitoring and reverse movement"""
    try:
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # Check first reed switch
            if check_reed_switch():
                logger.info("Reed switch 1 activated - stopping motor")
                set_motor("stop", 0)
                time.sleep(15)
                
                reverse_direction = "backward" if direction == "forward" else "forward"
                logger.info(f"Moving in reverse direction: {reverse_direction}")
                set_motor(reverse_direction, 100)
                time.sleep(2)
                set_motor("stop", 0)
                break
            
            # Check second reed switch only when moving forward
            if direction == "backward" and check_reed_switch_2():
                logger.info("Reed switch 2 activated while moving forward - stopping motor")
                set_motor("stop", 0)
                break
            
            set_motor(direction, 100)
            time.sleep(0.1)
        
        set_motor("stop", 0)
        return True
        
    except Exception as e:
        logger.error(f"Error in motor_action: {e}")
        set_motor("stop", 0)
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
            if motor_action("forward", 3):  # 3 seconds or until reed switch activates
                current_state = 'unlocked'
                logger.info("Successfully unlocked")
                return jsonify({'status': 'Success', 'action': 'unlocked'})
            else:
                logger.error("Failed to control motor")
                return jsonify({'error': 'Failed to control motor'}), 500
                
        # For lock command, move motor backward
        elif command == 'lock' and current_state == 'unlocked':
            if motor_action("backward", 3):  # 3 seconds or until reed switch activates
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
