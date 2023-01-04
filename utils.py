import http.client
import pandas as pd
from replit import db
from IPython.utils import tempdir
from constants import *
import os
import json

payload = ''
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
    "X-Riot-Token": os.environ['riotAPIKey']
}

def getPUUID(name:str):
  name = name.replace(' ', '%20')
  
  conn = http.client.HTTPSConnection("na1.api.riotgames.com")
  conn.request("GET", '/lol/summoner/v4/summoners/by-name/' + name, payload, headers)
  rees = conn.getresponse()
  data = rees.read()
  res = json.loads(data.decode("utf-8"))
  puuid = res['puuid']
  return puuid


def listOfLOLMatches(puuid:str):
  conn2 = http.client.HTTPSConnection("americas.api.riotgames.com")
  conn2.request("GET", '/lol/match/v5/matches/by-puuid/' + puuid + '/ids', payload, headers)

  res2 = conn2.getresponse()
  data2 = res2.read()
  res = json.loads(data2.decode("utf-8"))
  return res

def createDF(puuid:str, matches:list):
  if len(matches) > 2:
    matches = matches[:6]
    
  df = pd.DataFrame()

  for matchi in matches:
    temp = {}
    conn = http.client.HTTPSConnection("americas.api.riotgames.com")
    conn.request("GET", "/lol/match/v5/matches/" + matchi, payload, headers)
    res = conn.getresponse()
    res = res.read()
    res = json.loads(res.decode("utf-8"))

    temp['matchID'] = res['metadata']['matchId']
    temp['Gamemode'] = res['info']['gameMode']
    temp['Duration'] = res['info']['gameDuration']

    for player in res['info']['participants']:
      if player['puuid'] == puuid:
        temp['Champion'] = player['championName']
        temp['Role'] = player['role']
        temp['Won'] = player['win']
        temp["KDA"] = round(player['challenges']['kda'], 1)
        temp['Record'] = f"{player['kills']} - {player['deaths']} - {player['assists']}"
        temp['Gold_per_min'] = round(player['challenges']['goldPerMinute'], 1)
        temp['KillParticipation'] = round(player['challenges']['killParticipation'], 1)
        temp['CC'] = player['timeCCingOthers']
        temp['CS'] = player['totalMinionsKilled']
        temp['CSperMin'] = round((temp['CS'] / (temp['Duration'] / 60)), 1)
        temp['DMGperMin'] = round(player['challenges']['damagePerMinute'], 1)
        new_df = pd.DataFrame(temp, index=[0])
        df = pd.concat([df, new_df], ignore_index=True)
      else:
        continue

  return df