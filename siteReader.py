import requests
import re
import time

def getInput(response, inputName):
    regex = inputName + "[^>]*value=\""
    match = re.search(regex, response)
    if match: return re.search("[^\"]*", response[match.end():]).group()
    else: return ""

def getFormStats(r):
    return {
        '__VIEWSTATE':getInput(r.text,"__VIEWSTATE"),
        '__VIEWSTATEGENERATOR':getInput(r.text,"__VIEWSTATEGENERATOR"),
        '__EVENTVALIDATION':getInput(r.text,"__EVENTVALIDATION")
    }

class SiteReader:

    def __init__(self):
        url = "https://www12.honolulu.gov/csdarts/default.aspx"

        r = requests.get(url)
        payload = getFormStats(r)
        payload['btnAcceptTop'] = ""
        print("Grabbed homepage")

        time.sleep(0.5)
        self.prevResp =  requests.post(url, payload)

    def getDate(self):
        match = re.search("<span id=\"lblDate\">", self.prevResp.text)
        return re.search("[^<]*", self.prevResp.text[match.end():]).group()

    def getAppointments(self):
        tableRegex = "<table border=\"1\" cellpadding=\"1\" cellspacing=\"0\" width=\"100%\" style=\"table-layout:fixed;\">[\s\S]*</table>"
        rowRegex = "(<tr class=\"Table(Alt)?ItemLine\">[\s\S]*?<\/tr>)"
        cellRegex = "<td>[^M]*?</td>"

        table = re.search(tableRegex, self.prevResp.text)
        rows = re.findall(rowRegex, table.group())

        cellLists = []
        for (row,_) in rows: cellLists.append(re.findall(cellRegex, row))

        apptmts = []
        for i in range(len(cellLists[0])):
            apptmts.append([])
            for j in range(len(cellLists)):
                if not "None" in cellLists[j][i]:
                    numAvailable = getInput(cellLists[j][i], "dlstAppointment")
                    apptmts[i].append((j,numAvailable))

        return apptmts

    def loadFirstLocationPage(self, loc):
        url = "https://www12.honolulu.gov/csdarts/frmApptInt.aspx"

        payload = getFormStats(self.prevResp)
        payload['ddlLocation'] = loc
        payload['btnDateJump'] = "Go!"
        payload['__EVENTTARGET'] = ""
        payload['__EVENTARGUMENT'] = ""
        payload['__VIEWSTATEENCRYPTED'] = ""

        self.prevResp = requests.post(url, payload)

    def loadSpecDatePage(self, date):
        url = "https://www12.honolulu.gov/csdarts/frmApptInt.aspx"

        payload = getFormStats(self.prevResp)
        payload['ddlLocation'] = 0
        payload['__EVENTTARGET'] = "Calendar1"
        payload['__EVENTARGUMENT'] = date
        payload['__VIEWSTATEENCRYPTED'] = ""

        self.prevResp = requests.post(url, payload)
