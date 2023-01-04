from utils import *
from constants import *
import pandas as pd
from flask import (
  Flask,
  render_template,
  url_for,
  request
)
#import dash, plotly
#docker is containerization thing - when you have a program that has lots of dependencies/operating systems, etc, docker containerizes the software and makes it so other people that run it, run it exactly how you run it locally.

app = Flask(__name__) # our app instance

context = {
  'numMatches': 0,
  'IGN': '',
  'Winrate': '',
  'Record': '',
  'favChar': '',
  'favCharRecord': '',
  'matches': []
}

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/query/', methods=['GET', 'POST'])
def query():
  query = request.form['query'] 
  context['IGN'] = query
  try:
    df = getStats(query)
  except KeyError:
    return render_template('invalidIGN.html')

  context['numMatches'] = len(df)
  #winrate %
  winrate = round(df['Won'].mean() * 100, 1)
  context['Winrate'] = str(winrate) + '%'
  
  # record W-L
  numWins = df['Won'].sum()
  numLoss =  df['Won'].count() - numWins
  record = f"{numWins}W - {numLoss}L"
  context['Record'] = record

  #most played character and winrate
  ser = df['Champion'].value_counts()
  favChar = ser.index[0]
  timesPlayed = ser[0]
  context['favChar'] = favChar

  temp = df.query('Champion == @favChar')
  _numWins = temp['Won'].sum()
  _numLoss =  temp['Won'].count() - _numWins
  _record = f"{numWins}W - {numLoss}L"
  context['favCharRecord'] = _record

  df['Won'] = df['Won'].replace({True: 'Victory', False: 'Defeat'})
  context['matches'] = eachGame(df)
  
  return render_template('query.html', **context)

  
def getStats(name:str):
  puuid = getPUUID(name)
  matches = listOfLOLMatches(puuid)
  return createDF(puuid = puuid, matches = matches)


def eachGame(df:pd.DataFrame):
  listOfGames = df.to_dict('records')
  return listOfGames
  

def getFavoriteChamps(df:pd.DataFrame):
  ser = df['Champion'].value_counts()
  print(f'Your favorite character is {ser.index[0]}, you played them {ser[0]} time(s)')


if __name__ == '__main__':
  # df = getStats('rlzhang1310')
  # getFavoriteChamps(df)
  app.run(host='0.0.0.0', port=8080, debug=True)