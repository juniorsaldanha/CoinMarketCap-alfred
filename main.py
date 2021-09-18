
import sys, json, os
from workflow import Workflow3, web, ICON_WEB, ICON_WARNING, ICON_NETWORK
import threading

def get_web_data():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start':'1',
        'limit':'5000',
        'convert': os.getenv('currency').upper()
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': os.getenv('api_key'),
    }
    try:
        return web.get(url, params=parameters, headers=headers).json()
    except Exception as e:
        print(e)
        return {'data':[]}

# def download_logo(ticker_id, path_logo):
#     url = "https://s2.coinmarketcap.com/static/img/coins/64x64/"+str(ticker_id)+".png"
#     r = web.get(url, stream=True)
#     img = r.raw.read()
#     with open(path_logo, 'w') as f:
#         f.write(img)

def key_for_coin(ticker):
    return u'{} {}'.format(ticker['name'], ticker['symbol'])

def main(wf):
    currency = os.getenv('currency').upper()
    ticker = str(wf.args[0]).upper()

    json_data = wf.cached_data('coinmarketcap_cache', get_web_data, max_age=60 * 5)['data']
    items = wf.filter(ticker, json_data, key_for_coin)

    if not items:
        wf.add_item('No matches', icon=ICON_WARNING)
    for item in items:
        item_id = str(item['id'])
        path_logo = "images/"+item_id+".png"
        img_logo = path_logo if os.path.exists(path_logo) else ICON_NETWORK
        title = item['name'] + " (" + item['symbol'] + ")"
        subtitle = currency + " " + str(round(item['quote'][currency]['price'], 2))
        arg = "https://coinmarketcap.com/"+os.getenv('language').lower()+"/currencies/" + item['slug']
        wf.add_item(
            title=title,
            subtitle=subtitle,
            arg=arg,
            valid=True,
            icon=img_logo
        )
    wf.send_feedback()

if __name__ == '__main__':
    wf = Workflow3()
    sys.exit(wf.run(main))
