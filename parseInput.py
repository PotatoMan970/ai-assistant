import os
import speak
commandsToRunApp=["start","launch","open","run",]

commandsToCloseApp=["close","exit","terminate","kill",]


def parse(user_input):
    user_input_non_split = user_input.strip()
    user_input = user_input.strip().lower().split(" ")
    if user_input[0] in commandsToRunApp:
        appName = " ".join(user_input[1:])
        os.system(appName)
        speak.speak(f"Running {appName}")
    
    elif user_input[0] in commandsToCloseApp:
        appName = " ".join(user_input[1:])
        os.system(f"pkill {appName}")
        speak.speak(f"Closing {appName}")
    
    elif user_input[0] == "help":
        speak.speak("Commands to run an app: start, launch, open, run")
        speak.speak("Commands to close an app: close, exit, terminate, kill")