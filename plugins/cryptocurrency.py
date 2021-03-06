"""
cryptocurrency.py

A plugin that uses the CoinMarketCap JSON API to get values for cryptocurrencies.

Created By:
    - Luke Rogers <https://github.com/lukeroge>

Special Thanks:
    - https://coinmarketcap-nexuist.rhcloud.com/

License:
    GPL v3
"""
from urllib.parse import quote_plus
from datetime import datetime

import requests

from cloudbot import hook

API_URL = "https://coinmarketcap-nexuist.rhcloud.com/api/{}"


# aliases
@hook.command("bitcoin", "btc", autohelp=False)
def bitcoin(text):
    """ -- Returns current bitcoin value """
    # alias
    return crypto_command("btc", text)


@hook.command("litecoin", "ltc", autohelp=False)
def litecoin(text):
    """ -- Returns current litecoin value """
    # alias
    return crypto_command("ltc", text)


@hook.command("dogecoin", "doge", autohelp=False)
def dogecoin():
    """ -- Returns current dogecoin value """
    # alias
    return crypto_command("doge", text)


# main command
@hook.command("crypto", "cryptocurrency")
def crypto_command(text, currency):
    """ <ticker> -- Returns current value of a cryptocurrency """
    try:
        if currency == '':
            currency = 'usd'
        else:
            currency = currency.lower()
        encoded = quote_plus(text)
        request = requests.get(API_URL.format(encoded))
        request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        return "Could not get value: {}".format(e)

    data = request.json()

    if "error" in data:
        return "{}.".format(data['error'])

    updated_time = datetime.fromtimestamp(float(data['timestamp']))
    if (datetime.today() - updated_time).days > 2:
        # the API retains data for old ticker names that are no longer updated
        # in these cases we just return a "not found" message
        return "Currency not found."

    change = float(data['change'])
    if change > 0:
        change_str = "\x033 {}%\x0f".format(change)
    elif change < 0:
        change_str = "\x035 {}%\x0f".format(change)
    else:
        change_str = "{}%".format(change)

    if currency == 'gbp':
        currency_sign = '£'
    elif currency == 'eur':
        currency_sign = '€'
    else:
        currency_sign = '$'

    return "{} // \x0307{}{:,.2f}\x0f {} - {:,.7f} BTC // {} change".format(data['symbol'].upper(),
                                                                            currency_sign,
                                                                            float(data['price'][currency]),
                                                                            currency.upper(),
                                                                            float(data['price']['btc']),
                                                                            change_str)
