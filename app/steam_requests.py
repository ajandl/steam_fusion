from time import sleep
import requests
from app import app


def rate_limit(func):
    def wrapper(*args, **kwargs):
        sleep(2)
        return func(*args, **kwargs)
    return wrapper


class SteamRequests():
    API_URL = 'http://api.steampowered.com'
    STORE_URL = 'http://store.steampowered.com'
    steam_api_key = app.config['STEAM_API']
    PLAYER_SUMMARY = '/ISteamUser/GetPlayerSummaries/v0002/'
    OWNED_GAMES = '/IPlayerService/GetOwnedGames/v0001/'

    @rate_limit
    @classmethod
    def steam_store_helper(cls, endpoint_url, params=None):

        url = cls.STORE_URL + endpoint_url
        response = requests.get(url, params)

        return response.json()

    @rate_limit
    @classmethod
    def steam_api_helper(cls, endpoint_url, params):

        url = cls.API_URL + endpoint_url
        default_params = {'key': cls.steam_api_key, **params}
        response = requests.get(url, default_params).json()

        return response

    @classmethod
    def player(cls, steamid: str) -> dict:

        params = {'steamids': steamid}
        response = cls.steam_api_helper(cls.PLAYER_SUMMARY, params)

        return response['response']['players'][0]

    @classmethod
    def owned(cls, steamid: str) -> list:

        params = {'steamid': steamid}
        response = cls.steam_api_helper(cls.OWNED_GAMES, params)

        return response['response']['games']

    @classmethod
    def wishlist(cls, steamid: str) -> dict:

        response = cls.steam_store_helper(
            f'/wishlist/profiles/{steamid}/wishlistdata'
        )

        return response

    @classmethod
    def app_data(cls, app_id: str) -> str:

        params = {'appids': app_id}
        response = cls.steam_store_helper('/api/appdetails', params)

        if not response[app_id]['success']:
            return None

        return response[app_id]['data']
