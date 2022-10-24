from threading import Thread, Timer
from playsound import playsound

#Global variable 
voltage = 8
temperature = 90

# function to play sound  -- need to set variables, find wav files, and temperature/battery limits
def playSoundVolt():
    if (voltage < 10): 
        #wavFile = input("Enter a wav filename:")
        playsound(r'C:\\Users\fndoe\OneDrive\Desktop\PRE\Dashboard Code\Dashboard\Server\voltage_alert.wav')
        print("playing voltage sound w/ .wav")
    Timer(5, playSoundVolt).start()
    print("play sound voltage")


def playSoundTemp():
    if (temperature > 80):
        playsound(r'C:\\Users\fndoe\OneDrive\Desktop\PRE\Dashboard Code\Dashboard\Server\temperature_alert.wav')
        print("playing temperature sound w. .wav")
    Timer(60, playSoundTemp).start()
    print('play sound temperature')
    
    ## TRY FULL PATH FOR PHOTO

playSoundVolt()
playSoundTemp()