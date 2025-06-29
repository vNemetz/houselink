import cv2
import os
import numpy as np
import RPi.GPIO as GPIO
import time
import threading

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

# GPIO setup for reed switches
REED_PIN = 17  # GPIO17 para reed switch 1
REED_PIN_2 = 5  # GPIO27 para reed switch 2

GPIO.setup(REED_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(REED_PIN_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# GPIO setup for buttons
BUTTON_PIN_RECOGNITION = 26  # Botão para reconhecimento facial
BUTTON_PIN_REGISTER = 16    # Botão para cadastro de rosto

GPIO.setup(BUTTON_PIN_RECOGNITION, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_PIN_REGISTER, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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

def check_reed_switch():
    """Retorna True se o reed switch 1 está ativado (magneto presente)"""
    return GPIO.input(REED_PIN) == 0

def check_reed_switch_2():
    """Retorna True se o reed switch 2 está ativado (magneto presente)"""
    return GPIO.input(REED_PIN_2) == 0

def motor_action(direction: str, duration: int):
    """
    Move o motor na direção indicada, para e inverte se reed switch 1 ativar,
    ou para imediatamente se reed switch 2 ativar enquanto estiver indo para frente.
    """
    try:
        start_time = time.time()
        while time.time() - start_time < duration:
            # Se reed switch 1 ativar, para, espera 2s e inverte
            if check_reed_switch():
                print("Reed switch 1 ativado - parando motor")
                set_motor("stop", 0)
                time.sleep(2)
                reverse_direction = "backward" if direction == "forward" else "forward"
                print(f"Invertendo para: {reverse_direction}")
                set_motor(reverse_direction, 100)
                time.sleep(2)
                set_motor("stop", 0)
                return True
            # Se reed switch 2 ativar enquanto vai para frente, para imediatamente
            if direction == "forward" and check_reed_switch_2():
                print("Reed switch 2 ativado indo para frente - parando motor")
                set_motor("stop", 0)
                return True
            set_motor(direction, 100)
            time.sleep(0.1)
        set_motor("stop", 0)
        return True
    except Exception as e:
        print(f"Erro no motor_action: {e}")
        set_motor("stop", 0)
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
                    if motor_action("forward", 2):
                        print("Motor acionado para destravar.")
                        time.sleep(15)
                        if motor_action("backward", 1.95):
                            print("Motor acionado para travar.")
                        else:
                            print("Falha ao travar motor.")
                    else:
                        print("Falha ao destravar motor.")
                else:
                    print("Desconhecido")

    cap.release()

def wait_for_recognition_button():
    print("Aguardando o botão de reconhecimento ser pressionado...")
    while GPIO.input(BUTTON_PIN_RECOGNITION):
        time.sleep(0.05)
    print("Botão de reconhecimento pressionado!")
    time.sleep(0.3)  # debounce

def wait_for_register_button():
    print("Aguardando o botão de cadastro ser pressionado...")
    while GPIO.input(BUTTON_PIN_REGISTER):
        time.sleep(0.05)
    print("Botão de cadastro pressionado!")
    time.sleep(0.3)  # debounce

# Cleanup GPIO on program exit
def cleanup():
    try:
        pwm.stop()
        GPIO.cleanup()
    except Exception as e:
        print(f"Error during cleanup: {e}")

# Treinar o modelo inicialmente
train_model()

# Initialize motor to stopped state
try:
    set_motor("stop", 0)
except Exception as e:
    print(f"Error initializing motor: {e}")

def reconhecimento_via_botao():
    while True:
        wait_for_recognition_button()
        face_recognition()

def cadastro_via_botao():
    while True:
        wait_for_register_button()
        capture_multiple_faces()

# Inicie as duas threads dos botões antes do menu ou do loop principal
threading.Thread(target=reconhecimento_via_botao, daemon=True).start()
threading.Thread(target=cadastro_via_botao, daemon=True).start()

# Agora, se quiser, pode remover o menu e deixar só o loop de espera ou só o cleanup:
try:
    while True:
        time.sleep(1)  # Mantém o programa rodando
except KeyboardInterrupt:
    print("Encerrando programa.")
    cleanup()
