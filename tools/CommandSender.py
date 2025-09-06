import paho.mqtt.client as mqtt
import threading
import sys
import serial

BROKER = "192.168.1.31"
TOPIC = "/ESP00/#"
CMD_TOPIC = "/ESP00/cmd"
SERIAL_PORT = "COM7"
SERIAL_BAUDRATE = 57600

adresse_3_octets = None  # Variable globale pour stocker l'adresse

def afficher_aide():
    print("""
CommandSender MQTT & Serial - Contrôle RFLink
---------------------------------------------
Touches disponibles :
  a : Saisir une adresse hexadécimale sur 3 octets (6 caractères)
  x : Envoyer "10;PING;" (MQTT & Série)
  p : Envoyer "10;RTS;<adresse>;0004;PAIR" (si adresse saisie)
  c : Envoyer "10;RTSCLEAN"
  u : Envoyer "10;RTS;<adresse>;0;UP;" (si adresse saisie)
  d : Envoyer "10;RTS;<adresse>;0;DOWN;" (si adresse saisie)
  q : Quitter le script
Les messages MQTT reçus sur /ESP00/# seront affichés avec [MQTT].
Les messages reçus sur le port série seront affichés avec [Serial].
""")

def on_connect(client, userdata, flags, rc):
    print("[MQTT] Connecté au broker avec le code de retour", rc)
    client.subscribe(TOPIC)
    print(f"[MQTT] Abonné au topic {TOPIC}")

def on_message(client, userdata, msg):
    print(f"[MQTT] [{msg.topic}] {msg.payload.decode('utf-8', errors='replace')}")

def listen_keyboard(client, ser):
    global adresse_3_octets
    while True:
        key = sys.stdin.read(1)
        if key.lower() == 'x':
            commande = "10;PING;"
            client.publish(CMD_TOPIC, commande)
            if ser:
                ser.write((commande + "\n").encode())
            print("[MQTT][Serial] PING envoyé")
        elif key.lower() == 'a':
            addr = input("Entrez une adresse hexadécimale sur 3 octets (6 caractères, ex : 0f0f0f) : ")
            if len(addr) == 6 and all(c in "0123456789abcdefABCDEF" for c in addr):
                adresse_3_octets = addr.upper()
                print(f"Adresse saisie : {adresse_3_octets}")
            else:
                print("Adresse invalide. Veuillez entrer exactement 6 caractères hexadécimaux.")
        elif key.lower() == 'p':
            if adresse_3_octets:
                commande = f"10;RTS;{adresse_3_octets};0004;PAIR"
                client.publish(CMD_TOPIC, commande)
                if ser:
                    ser.write((commande + "\n").encode())
                print(f"[MQTT][Serial] Commande envoyée : {commande}")
            else:
                print("Aucune adresse saisie. Appuyez sur 'a' pour entrer une adresse avant d'utiliser 'p'.")
        elif key.lower() == 'c':
            commande = "10;RTSCLEAN"
            client.publish(CMD_TOPIC, commande)
            if ser:
                ser.write((commande + "\n").encode())
            print("[MQTT][Serial] Commande envoyée : 10;RTSCLEAN")
        elif key.lower() == 'u':
            if adresse_3_octets:
                commande = f"10;RTS;{adresse_3_octets};0;UP;"
                client.publish(CMD_TOPIC, commande)
                if ser:
                    ser.write((commande + "\n").encode())
                print(f"[MQTT][Serial] Commande envoyée : {commande}")
            else:
                print("Aucune adresse saisie. Appuyez sur 'a' pour entrer une adresse avant d'utiliser 'u'.")
        elif key.lower() == 'd':
            if adresse_3_octets:
                commande = f"10;RTS;{adresse_3_octets};0;DOWN;"
                client.publish(CMD_TOPIC, commande)
                if ser:
                    ser.write((commande + "\n").encode())
                print(f"[MQTT][Serial] Commande envoyée : {commande}")
            else:
                print("Aucune adresse saisie. Appuyez sur 'a' pour entrer une adresse avant d'utiliser 'd'.")
        elif key.lower() == 'h':
            afficher_aide()
        elif key.lower() == 'q':
            print("Arrêt du script demandé par l'utilisateur.")
            client.disconnect()
            if ser:
                ser.close()
            sys.exit(0)

def listen_serial(ser):
    while True:
        try:
            line = ser.readline()
            if line:
                print(f"[Serial] {line.decode(errors='replace').rstrip()}")
        except Exception as e:
            print(f"[Serial] Erreur : {e}")
            break

if __name__ == "__main__":
    afficher_aide()
    # Initialisation du port série
    try:
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=1)
        print(f"[Serial] Port série {SERIAL_PORT} ouvert à {SERIAL_BAUDRATE} bauds.")
    except Exception as e:
        print(f"[Serial] Impossible d'ouvrir le port série {SERIAL_PORT} : {e}")
        ser = None

    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, 1883, 60)

    # Thread clavier
    threading.Thread(target=listen_keyboard, args=(client, ser), daemon=True).start()
    # Thread série (si dispo)
    if ser:
        threading.Thread(target=listen_serial, args=(ser,), daemon=True).start()

    client.loop_forever()