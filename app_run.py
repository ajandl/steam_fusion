from app import app, setup_app, routes  # noqa


if __name__ == '__main__':
    app = setup_app(app)
    # from app import routes  # noqa
    app.run(debug=True)
