import cv2
import os
import numpy as np
import RPi.GPIO as GPIO
import time

# Force OpenCV to use headless mode
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Diretório do banco de dados
db_path = "face_db/"
os.makedirs(db_path, exist_ok=True)
path ='/home/rasp/Facial-Recognition/haarcascade_frontalface_default.xml'
label_ids = {}

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

# Carregar classificador Haarcascade
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
if face_cascade.empty():
    raise Exception("Erro ao carregar o classificador Haarcascade.")

# Criar reconhecedor LBPH
recognizer = cv2.face.LBPHFaceRecognizer_create()

def load_training_data(data_folder):
    global label_ids
    faces, labels = [], []
    label_ids = {}
    current_id = 0

    if not os.listdir(data_folder):
        print(f"A pasta '{data_folder}' está vazia.")
        return faces, labels

    for root, _, files in os.walk(data_folder):
        for file in files:
            if file.endswith(("png", "jpg")):
                path = os.path.join(root, file)
                label = os.path.basename(root).lower()

                if label not in label_ids:
                    label_ids[label] = current_id
                    current_id += 1

                img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    print(f"Erro ao carregar {path}")
                    continue

                img = cv2.resize(img, (100, 100))
                faces.append(img)
                labels.append(label_ids[label])

    return faces, labels

def capture_multiple_faces(num_samples=30):
    print(f"Capturando {num_samples} imagens. Posicione o rosto na câmera.")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Erro: Não foi possível abrir a câmera.")

    user_id = len(os.listdir(db_path)) + 1
    name = f"user{user_id}"
    user_folder = os.path.join(db_path, name)
    os.makedirs(user_folder, exist_ok=True)

    count = 0

    while count < num_samples:
        ret, frame = cap.read()
        if not ret:
            print("Erro ao capturar frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            face_img = gray[y:y+h, x:x+w]
            face_img = cv2.resize(face_img, (100, 100))
            save_path = os.path.join(user_folder, f"{count + 1}.jpg")
            cv2.imwrite(save_path, face_img)
            count += 1

    cap.release()
    train_model()

def train_model():
    global recognizer, label_ids
    faces, labels = load_training_data(db_path)
    if faces:
        recognizer.train(faces, np.array(labels))
        print("Reconhecedor treinado com sucesso!")
    else:
        print("Nenhum dado de treinamento encontrado.")

def set_motor(direction: str, speed: int):
    """Control motor direction and speed"""
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

        pwm.ChangeDutyCycle(speed)
        return True
    except Exception as e:
        print(f"Error controlling motor: {e}")
        return False

def face_recognition():
    print("Iniciando reconhecimento facial.")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Erro: Não foi possível abrir a câmera.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro ao capturar frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            face_img = gray[y:y+h, x:x+w]
            face_img = cv2.resize(face_img, (100, 100))

            if label_ids:
                label, confidence = recognizer.predict(face_img)
                if confidence < 80 and label in label_ids.values():
                    name = list(label_ids.keys())[list(label_ids.values()).index(label)]
                    print("Reconhecido")

                    # Activate motor to unlock
                    if set_motor("forward", 100):
                        time.sleep(3)  # Run motor for 3 seconds
                        set_motor("stop", 0)  # Stop motor
                        print("Motor unlocked successfully.")

                        # Wait for 20 seconds
                        time.sleep(15)

                        # Activate motor to lock
                        if set_motor("backward", 100):
                            time.sleep(3)  # Run motor for 3 seconds
                            set_motor("stop", 0)  # Stop motor
                            print("Motor locked successfully.")
                        else:
                            print("Failed to lock motor.")
                    else:
                        print("Failed to unlock motor.")
                else:
                    print("Desconhecido")

    cap.release()

# Cleanup GPIO on program exit
def cleanup():
    try:
        pwm.stop()
        GPIO.cleanup()
    except Exception as e:
        print(f"Error during cleanup: {e}")

# Treinar o modelo inicialmente
train_model()

# Menu via terminal
try:
    # Initialize motor to stopped state
    set_motor("stop", 0)
except Exception as e:
    print(f"Error initializing motor: {e}")

while True:
    print("\n--- Menu ---")
    print("1. Cadastrar novo rosto")
    print("2. Iniciar reconhecimento facial")
    print("3. Sair")
    choice = input("Escolha uma opção (1/2/3): ")

    if choice == '1':
        capture_multiple_faces()
    elif choice == '2':
        face_recognition()
    elif choice == '3':
        print("Encerrando programa.")
        cleanup()
        break
    else:
        print("Opção inválida. Tente novamente.")
