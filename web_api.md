## Steam Web API
- Documentation: https://developer.valvesoftware.com/wiki/Steam_Web_API
- Base URL: http://api.steampowered.com/IPlayerService/
- Useful endpoints:
  - GetOwnedGames (v0001) - Gets a list of games owned by a user.

## Steam Storm Web API
- Documentation (unofficial): https://wiki.teamfortress.com/wiki/User:RJackson/StorefrontAPI
- Base URL: http://store.steampowered.com/
- Useful endpoints:
  - appdetails - Gets detailed information for an appid.
  - wishlist (wishlist/profiles/{{ userid }}/wishlistdata/) - Gets games on a user's wishlist 