from app import app
from flask import jsonify, request
from app.list_entries_model import ListEntry
from app.list_roles_model import ListRoles
from app.lists_model import ListsModel
from app.steam_games_model import SteamGame
from app.users_model import User
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    unset_jwt_cookies,
    get_jwt,
)
from datetime import datetime, timedelta, timezone
from app import db
import json
from app.steam_requests import (
    get_player_summary,
    get_owned,
    get_app_name,
    get_wishlist,
)


def get_list_entries(user: User, list_model: ListsModel) -> dict:
    """Return the entries on a User's List

    Positional arguments:
    user: The user associated with the entries
    list_model: The list associated with the entries

    Returns:
    dict: Keys - steam app ids; values - ListEntry
    """
    # This is currently using the user_id to filter, but the user_id in the 
    # ListEntry table is supposed to be the user that added the game to the 
    # list, not the user that the entry is associated with.  Need to do the 
    # filtering in another way.
    owned_entries = (
        ListEntry.query
        .join(ListsModel)
        .filter(ListEntry.list_id == list_model.list_id)
        .filter(ListEntry.user_id == user.user_id)
        .all()
    )
    owned_entries_dict = {}
    # Try using dictionary comprehension 
    for entry in owned_entries:
        owned_entries_dict[str(entry.steam_app_id)] = entry
    entries_dict = {str(entry.steam_app_id): entry for entry in owned_entries} 

    return owned_entries_dict


def get_steam_games() -> dict:
    steam_game_dict = {}
    steam_game_query = SteamGame.query.all()

    # Use dictionary comprehension
    for steam_game in steam_game_query:
        steam_game_dict[str(steam_game.steam_app_id)] = steam_game

    return steam_game_dict


def create_entry(
    user: User,
    app: SteamGame,
    list_model: ListsModel
) -> ListEntry:

    new_entry = ListEntry(
        user_id=user.user_id,
        steam_app_id=app.steam_app_id,
        list_id=list_model.list_id,
    )
    new_entry.user = user
    new_entry.app = app
    new_entry.list_relationship = list_model

    return new_entry


@app.route('/')
def homepage():
    # return render_template('main.html')
    return {'key1': 'val1', 'key2': 'val2'}


@app.route("/login", methods=["POST"])
def login():
    current_username = request.json.get('username')
    current_password = request.json.get('password')

    user = User.query.filter_by(username=current_username).first()

    if user is None or not user.check_password(current_password):
        return jsonify(msg='User not validated.'), 401

    access_token = create_access_token(identity=user.user_id)
    return jsonify(access_token=access_token), 200


@app.route("/logout", methods=["POST"])
def logout():
    response = jsonify(msg="Logout successful")
    unset_jwt_cookies(response)
    return response, 200


@app.route("/register", methods=["POST"])
def register():
    new_username = request.json.get('username')
    new_user_password = request.json.get('password')
    new_user_email = request.json.get('email')
    # if not all(username, password, email):
    # ...
    if (
        new_username is None or
        new_user_password is None or
        new_user_email is None
    ):
        return jsonify(msg='Missing required information'), 403

    # Does user already exist?
    current_user_list = User.query.filter_by(username=new_username).all()
    for u in current_user_list:
        # I don't think I need to check the email if the user already exists
        if new_user_email == u.email:
            return jsonify(msg='Username and email already exist.'), 409

    new_user = User(username=new_username, email=new_user_email)
    new_user.set_password(new_user_password)

    db.session.add(new_user)
    db.session.commit()
    return (
        jsonify(
            msg='User successfully created',
            username=new_user.username,
        ),
        200,
    )


@app.route("/checktoken", methods=["GET"])
@jwt_required()
def checktoken():
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(user_id=current_user_id).first()
    return (
        jsonify(
            logged_in_as_user_id=current_user_id,
            username=current_user.username,
        ),
        200
    )


@app.route("/set_steam", methods=["POST"])
@jwt_required()
def set_steam():
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(user_id=current_user_id).first()

    steamid = request.args.get('steamid')

    # Use /GetPlayerSummaries/ to check steamid and get steam persona
    try:
        steam_name = get_player_summary(steamid)['personaname']
    except IndexError:
        return jsonify(msg="IndexError: Steam ID invalid"), 403
    except KeyError:
        return jsonify(msg="KeyError: Steam ID invalid"), 403

    current_user.set_steam(steamid=steamid, steam_name=steam_name)
    db.session.commit()
    return jsonify(msg="Steam identity successfully updated"), 200


# Could also move these into a special class.  Search enums on google.
OWNED = 'owned'
WISHLIST = 'wishlist'
def update_steam_lists(user: User, list_type):
    # Should check dictionary for the functions instead of using if statements
    if list_type == OWNED:
        get_steam_list = get_owned
    elif list_type == WISHLIST:
        get_steam_list = get_wishlist

    user_role_owned = (
        ListRoles.query
        .join(ListsModel)
        .filter(ListRoles.user_id == user.user_id)
        .filter(ListsModel.list_name == list_type)
        .first()
    )

    if user_role_owned is None:
        # This part could be moved to it's own function for create_list
        new_list = ListsModel(list_name=list_type)
        new_role = ListRoles(
            user_id=user.user_id,
            permission_lvl='owner',
        )
        new_role.list_relationship = new_list
        db.session.add(new_list)
        db.session.add(new_role)
        user_role_owned = new_role
        list_owned = new_list
    else:
        list_owned = (
            ListsModel.query
            .filter_by(list_id=user_role_owned.list_id)
            .first()
        )

    steam_list = get_steam_list(user.steamid)
    handlers = {
        'wishlist': lambda sl: [item for item in sl],
        'owned': lambda sl: [str(item['appid']) for item in sl]
    }
    app_id_list = handlers[list_type](steam_list)
    # if list_type == 'wishlist':
    #     app_id_list = []
    #     for itm in steam_list:
    #         app_id_list.append(itm)
    # elif list_type == 'owned':
    #     app_id_list = []
    #     for itm in steam_list:
    #         app_id_list.append(str(itm['appid']))

    steam_game_dict = get_steam_games()
    entries_dict = get_list_entries(user, list_owned)

    for app_id in app_id_list:

        if app_id in entries_dict.keys():
            print(f"{app_id} already in {entries_dict[app_id]}")
        elif app_id in steam_game_dict.keys():
            new_entry = create_entry(
                user,
                steam_game_dict[app_id],
                list_owned,
            )

            db.session.add(new_entry)
            print(f"Added {new_entry}")
        else:
            # Can this be simplified with helper functions?
            print(f"getting data for app id: {app_id}")
            app_data = get_app_name(str(app_id))
            if app_data is not None:
                app_name = app_data['name']
                new_steam_app = SteamGame(
                    steam_app_id=app_id,
                    game_title=app_name,
                )
                new_entry = create_entry(
                    user,
                    new_steam_app,
                    list_owned
                )
                db.session.add(new_steam_app)
                db.session.add(new_entry)
    # app_dict now has all of the apps owned by current_user.  Need to compare
    # to what we have stored in the db.

    db.session.commit()
    entries_dict = get_list_entries(user, list_owned)
    app_dict = {}
    for entry in entries_dict.values():
        app_id = entry.steam_app_id
        # There can be a KeyError on the next line if a game was added to the
        # db on L241. Error will not be present on 2nd execution.
        # I think this will work now.
        app_dict[app_id] = entries_dict[app_id].game_title

    return app_dict


@app.route("/update_owned_list", methods=["GET"])
@jwt_required()
def update_owned_list():
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(user_id=current_user_id).first()

    app_dict = update_steam_lists(current_user, 'owned')

    return jsonify(app_dict)


@app.route("/update_wl_list", methods=["GET"])
@jwt_required()
def update_wl_list():
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(user_id=current_user_id).first()

    app_dict = update_steam_lists(current_user, 'wishlist')

    return app_dict


@app.after_request
def refresh_token(response):
    try:
        exp_timestamp = get_jwt()['exp']
        now = datetime.now(timezone.utc)
        # TODO Move expiration time to config.py
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))

        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data['access_token'] = access_token
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        return response
