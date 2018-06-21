import requests
import datetime
import json

def get_hit_list():
    today = datetime.datetime.now()
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    last_week = today - datetime.timedelta(days=1)
    q_params={'order':'desc', 
              'limit':50, 
              'service':'triplej', 
              'from':last_week.strftime('%Y-%m-%dT%H:%M:%SZ'), 
              'to':today.strftime('%Y-%m-%dT%H:%M:%SZ')}

    hit_html = requests.get('https://music.abcradio.net.au/api/v1/recordings/plays.json', params= q_params)

    data = json.loads(hit_html.text)
    songs = data['items']
    res = []
    for rank, s in enumerate(songs):
        s_dict = {}
        s_dict['artist'] = ", ".join([a['name'] for a in s['artists']])
        s_dict['title'] = s['title']
        try:
            s_dict['album'] = s['releases'][0]['title']
        except IndexError:
            s_dict['album'] = 'Unreleased'
        res.append(s_dict)
    return res

def main():
    res = get_hit_list()
    for r in res:
        print(r) 

if __name__ == "__main__":
    main()