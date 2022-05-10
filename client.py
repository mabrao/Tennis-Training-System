import socket
import keyboard
from os.path import exists

PORT = 80
SERVER = '192.168.4.1' #IP address of where the server is being hosted
FORMAT = 'utf-8'
SEND_MSG = b'1'

#socket of type that connects to ipv4 and data set to streaming:
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

def write(count):
    while True:
        s.send(SEND_MSG)

        if keyboard.is_pressed('esc'):
            print('[STOPPED RECORDING]')
            break
        
        #blocking:
        msg = s.recv(1024).decode(FORMAT) #buffer (maximum amount of data (bytes) to be received at once)
        
        try:
            if exists(f'./sensor_data/backhand{count}.txt'): #if the file exists write to it in append mode
                with open(f'./sensor_data/backhand{count}.txt', 'a') as f:
                    print('[RECORDING DATA]')
                    f.write(msg)
            else: #if it doesn't exist create the file and write to it
                with open(f'./sensor_data/backhand{count}.txt', 'w') as f:
                    print('[RECORDING DATA]')
                    f.write(msg)
        except FileNotFoundError:
            print('The sensor_data directory does not exist')



if __name__ == '__main__':
    print('[STARTING]')
    s.connect((SERVER, PORT)) #ip, port
    print(f'[CONNECTED TO LOCAL SERVER {SERVER} ON PORT {PORT}]')
    print('[PRESS R TO RECORD AND ESC TO STOP RECORDING]')

    count = 0
    while True:
        if keyboard.is_pressed('r'):
            count += 1
            write(count)
        


