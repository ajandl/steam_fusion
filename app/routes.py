from app import app
from flask import jsonify, request
from app.users_model import User
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import unset_jwt_cookies
from flask_jwt_extended import get_jwt
from datetime import datetime, timedelta, timezone
from app import db
import json
from app.steam_requests import SteamRequests
from app.route_helpers import update_steam_lists


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
    if not all(new_username, new_user_password, new_user_email):
        return jsonify(msg='Missing required information'), 403

    # Does user already exist?
    current_user_list = User.query.filter_by(username=new_username).first()
    if current_user_list:
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
        steam_name = SteamRequests.player(steamid)['personaname']
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
        timeout = app.config['TOKEN_TIMEOUT']
        target_timestamp = datetime.timestamp(now + timedelta(minutes=timeout))

        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data['access_token'] = access_token
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        return response
