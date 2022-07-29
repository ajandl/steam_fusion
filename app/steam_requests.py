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


def get_owned(steamid: str) -> list:

    r = requests.get(
        r'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/',
        params={'key': app.config['STEAM_API'], 'steamid': steamid}
    ).json()

    return r['response']['games']


def get_app_name(app_id: str) -> str:

    r = requests.get(
        r'http://store.steampowered.com/api/appdetails',
        params={'appids': app_id}
    ).json()

    return r[app_id]['data']
