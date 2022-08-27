from app import app
from flask import jsonify, request
from app.models import (
    User,
    SteamGame,
    ListEntry,
    ListRoles,
    ListsModel,
)
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
    owned_entries = (
        ListEntry.query
        .join(ListsModel)
        .filter(ListEntry.list_id == list_model.list_id)
        .filter(ListEntry.user_id == user.user_id)
        .all()
    )
    owned_entries_dict = {}
    for entry in owned_entries:
        owned_entries_dict[str(entry.steam_app_id)] = entry

    return owned_entries_dict


def get_steam_games() -> dict:
    steam_game_dict = {}
    steam_game_query = SteamGame.query.all()
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
    if (
        new_username is None or
        new_user_password is None or
        new_user_email is None
    ):
        return jsonify(msg='Missing required information'), 403

    # Does user already exist?
    current_user_list = User.query.filter_by(username=new_username).all()
    for u in current_user_list:
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


@app.route("/update_owned_list", methods=["GET"])
@jwt_required()
def update_owned_list():
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(user_id=current_user_id).first()

    user_role_owned = (
        ListRoles.query
        .join(ListsModel)
        .filter(ListRoles.user_id == current_user_id)
        .filter(ListsModel.list_name == 'owned')
        .first()
    )

    if user_role_owned is None:
        new_list = ListsModel(list_name='owned')
        new_role = ListRoles(
            user_id=current_user_id,
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

    steam_owned_list = get_owned(current_user.steamid)

    steam_game_dict = get_steam_games()
    owned_entries_dict = get_list_entries(current_user, list_owned)

    for game in steam_owned_list:
        app_id = str(game['appid'])

        if app_id in owned_entries_dict.keys():
            print(f"{app_id} already in {owned_entries_dict[app_id]}")
        elif app_id in steam_game_dict.keys():
            new_entry = create_entry(
                current_user,
                steam_game_dict[app_id],
                list_owned,
            )

            db.session.add(new_entry)
            print(f"Added {new_entry}")
        else:
            print(f"getting data for app id: {app_id}")
            app_data = get_app_name(str(app_id))
            if app_data is not None:
                app_name = app_data['name']
                new_steam_app = SteamGame(
                    steam_app_id=app_id,
                    game_title=app_name,
                )
                new_entry = create_entry(
                    current_user,
                    new_steam_app,
                    list_owned
                )
                db.session.add(new_steam_app)
                db.session.add(new_entry)
    # app_dict now has all of the apps owned by current_user.  Need to compare
    # to what we have stored in the db.

    db.session.commit()
    owned_entries_dict = get_list_entries(current_user, list_owned)
    app_dict = {}
    for entry in owned_entries_dict.values():
        app_id = entry.steam_app_id
        app_dict[app_id] = steam_game_dict[app_id].game_title

    return jsonify(app_dict)


@app.after_request
def refresh_token(response):
    try:
        exp_timestamp = get_jwt()['exp']
        now = datetime.now(timezone.utc)
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
