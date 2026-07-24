import os

appNametoSystemName = {
    "firefox": "firefox",
    "browser": "firefox",
    "terminal": "kitty",
    "music player": "spotify",
    "spotify": "spotify",
    "music": "spotify",
    "video player": "vlc",
    "code editor": "code",
    "code": "code",
    "vs code": "code",
}

def launch_app(appName):
    appName = appName.lower().replace("my" , "").replace("the" , "").strip().replace("please" , "").strip()
    if appName in appNametoSystemName:
        os.system(appNametoSystemName[appName])
    else:
        print("App not found")