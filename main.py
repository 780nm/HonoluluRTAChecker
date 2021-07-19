from siteReader import SiteReader
from datetime import datetime
import RPi.GPIO as GPIO
import time
import webbrowser

#--------------------------------------------------
# CONFIG
#--------------------------------------------------

buzzerPin = 8

alertRange = 20

# If the first available appointment at these locations is within the above number of days, alert
alertLocs = [
    # 'location code'
    '1','6'
]

#--------------------------------------------------
# CONSTANTS
#--------------------------------------------------

rows = [
    "08:00 AM",
    "08:30 AM",
    "09:00 AM",
    "09:30 AM",
    "10:00 AM",
    "10:30 AM",
    "11:00 AM",
    "11:30 AM",
    "12:00 PM",
    "12:30 PM",
    "01:00 PM",
    "01:30 PM",
    "02:00 PM",
    "02:30 PM",
    "03:00 PM",
    "03:30 PM"
]

sites = {
    '1':'Sheridan',
    '2':'Kapolei ',
    '6':'Koolau  ',
    '4':'Wahiawa ',
    '5':'Waianae '
}

#--------------------------------------------------
# HELPERS
#--------------------------------------------------

GPIO.setmode(GPIO.BOARD)
GPIO.setup(buzzerPin,GPIO.OUT)
buzzer = GPIO.PWM(buzzerPin, 440)

global alertFlag
alertFlag = False

def alert():
    # # Buzzer or what have you
    print("ALERT!")

    buzzer.start(50)
    for i in range (5):
        buzzer.ChangeFrequency(880)
        time.sleep(0.5)
        buzzer.ChangeFrequency(440)
        time.sleep(0.5)
    buzzer.stop()

def checkReports(code, date):
    global alertFlag
    delta = datetime.strptime(date,"%m/%d/%Y") - datetime.now()
    if code in alertLocs and delta.days <= alertRange:
        alertFlag = True

def generateFirstAvailableReport():
    print("-------------------------------------------------")
    print("Earliest available appointments:")
    for index, code in enumerate(sites):
        s.loadFirstLocationPage(code)
        appointments = s.getAppointments()
        if len(appointments[index]) == 0:
            print(sites[code] + ": None available")
        else:
            date = s.getDate()
            (row,number) = appointments[index][0]
            print(sites[code] + ": " + number + " available at " + rows[row] + " on " + date)

        checkReports(code, date)

        time.sleep(0.5)

#--------------------------------------------------
# LOOP
#--------------------------------------------------

buzzer.start(50)
time.sleep(1)
buzzer.stop()

print("Done GPIO setup")

s = SiteReader()
print("Done initializing")
time.sleep(0.5)

while True:
    alertFlag = False

    print("")
    print("=================================================")
    print("")

    current_time = time.localtime()
    timeStr = time.strftime("%d %b %Y %H:%M:%S GMT", current_time)
    print("Checked at: " + timeStr)

    generateFirstAvailableReport()
    if alertFlag: alert()

    time.sleep(180)
