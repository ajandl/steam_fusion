import requests
from app import app


def get_player_summary(steamid: str) -> dict:

    r = requests.get(
        r'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/',
        params={'key': app.config['STEAM_API'], 'steamids': steamid}
    ).json()

    return r['response']['players'][0]


def get_wishlist(steamid: str) -> dict:

    r = requests.get(
        (r'http://store.steampowered.com/'
         fr'wishlist/profiles/{steamid}/wishlistdata')
    ).json()

    return r
