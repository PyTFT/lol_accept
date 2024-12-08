import re
import os
import json
import base64
import urllib3
import requests
import time

class LOL:
    def __init__(self):
        urllib3.disable_warnings()
        result = os.popen('wmic PROCESS WHERE name="LeagueClientUx.exe" GET commandline')
        result = result.read().replace(' ', '').split(' ')
        token = re.findall(re.compile(r'"--remoting-auth-token=(.*?)"'), result[0])
        self.__port = re.findall(re.compile(r'"--app-port=(.*?)"'), result[0])
        self.__token = base64.b64encode(("riot:" + token[0]).encode("UTF-8")).decode("UTF-8")
        self.__headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Basic " + self.__token
        }
        self.__url = 'https://127.0.0.1:' + str(self.__port[0])

    def get(self, url):
        return requests.get(url=self.__url + url, headers=self.__headers, verify=False).json()

    # def post(self, url):
    #     return requests.post(url=self.__url + url, headers=self.__headers, verify=False).json()
    def post(self, url):
        response = requests.post(url=self.__url + url, headers=self.__headers, verify=False)
        if response.status_code == 204:
            # print("No content to return")
            return None
        if not response.text:
            # print("Received empty response")
            return None
        try:
            return response.json()
        except json.JSONDecodeError:
            print("Failed to decode JSON")
            return None

    def accept_match(self):
        url_one = "/lol-matchmaking/v1/ready-check/accept"
        return self.post(url_one)

    def check_gameflow_phase(self):
        url = "/lol-gameflow/v1/gameflow-phase"
        return self.get(url)
    
lol = LOL()

while True:
    print('等待匹配成功')
    while True:
        try:
            gamestatus = lol.check_gameflow_phase()
        except:
            time.sleep(10)
            try:
                lol = LOL()
            except:
                gamestatus == 'Reconnect'

        if gamestatus == "ReadyCheck":    # InProgress游戏中
            lol.accept_match()
        elif gamestatus == 'InProgress':
            break   
        time.sleep(1)
    print("等待新对局开始")

    while True:
            gamestatus = lol.check_gameflow_phase()
            if gamestatus == 'InProgress': 
                time.sleep(5)
            elif gamestatus == 'Reconnect':
                time.sleep(10)
            else:
                break
