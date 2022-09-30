from app.list_entries_model import ListEntry
from app.list_roles_model import ListRoles
from app.lists_model import ListsModel
from app.steam_games_model import SteamGame
from app.users_model import User
from app.steam_requests import SteamRequests
from app import db


def get_list_entries(user: User, list_model: ListsModel) -> dict:
    """Return the entries on a User's List

    Positional arguments:
    user: The user associated with the entries
    list_model: The list associated with the entries

    Returns:
    dict: Keys - steam app ids; values - ListEntry
    """

    # The following query should return 1 role, NoResultFound error, or
    # MultipleResultsFound Error. The route is expected to handle these errors
    # by returning appropriate HTTP error codes. Assuming that a user is only
    # ever granted a single permission level on a list (something we can
    # enforce), then no further checks are required here to determine if the
    # user has the appropriate permission level.
    ListRoles.query.filter_by(
        list_id=list_model.list_id,
        user_id=user.user_id,
    ).one()

    # If no errors were raised, then the user must have permission to view the
    # list.
    list_entries = (
        ListEntry.query
        .join(ListsModel)
        .filter(ListEntry.list_id == list_model.list_id)
        .all()
    )
    entries_dict = {}
    # Try using dictionary comprehension
    for entry in list_entries:
        entries_dict[str(entry.steam_app_id)] = entry
    entries_dict = {
        str(entry.steam_app_id): entry for entry in list_entries
    }

    return entries_dict


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


def update_steam_lists(user: User, list_type: str) -> dict:

    get_steam_list = SteamRequests.list_methods.get(list_type)
    # should raise an error if get_steam_list is none.

    user_role = (
        ListRoles.query
        .join(ListsModel)
        .filter(ListRoles.user_id == user.user_id)
        .filter(ListsModel.list_name == list_type)
        .first()
    )

    if user_role is None:
        # This part could be moved to it's own function for create_list
        new_list = ListsModel(list_name=list_type)
        new_role = ListRoles(
            user_id=user.user_id,
            permission_lvl='owner',
        )
        new_role.list_relationship = new_list
        db.session.add(new_list)
        db.session.add(new_role)
        user_role = new_role
        list_owned = new_list
    else:
        list_owned = (
            ListsModel.query
            .filter_by(list_id=user_role.list_id)
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
            app_data = SteamRequests.app_data(str(app_id))
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
    steam_game_dict = get_steam_games()
    app_dict = {}
    for entry in entries_dict.values():
        app_id = entry.steam_app_id
        app_dict[app_id] = steam_game_dict[app_id].game_title

    return app_dict
