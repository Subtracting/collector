import dash
from flask import Flask
from flask.helpers import get_root_path
from flask_login import login_required
import dash_bootstrap_components as dbc

from config import BaseConfig  # type: ignore


def create_app():
    server = Flask(__name__, static_folder="/collector/static")
    server.config.from_object(BaseConfig)

    register_dashapps(server)
    register_extensions(server)
    register_blueprints(server)

    return server


def register_dashapps(app):
    from app.dashapp.callbacks import layout, register_callbacks, options
    from app.dashapp.callbacks import register_callbacks

    options = options()

    # Meta tags for viewport responsiveness
    meta_viewport = {
        "name": "viewport",
        "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}

    dashapp = dash.Dash(__name__,
                        server=app,
                        external_stylesheets=[dbc.themes.DARKLY],
                        url_base_pathname='/dashboard/',
                        assets_folder=get_root_path(
                            __name__) + '/assets/',
                        meta_tags=[meta_viewport])

    with app.app_context():
        dashapp.title = 'Logger'
        dashapp.layout = layout(options)
        register_callbacks(dashapp, options)

    _protect_dashviews(dashapp)


def _protect_dashviews(dashapp):
    for view_func in dashapp.server.view_functions:
        if view_func.startswith(dashapp.config.url_base_pathname):
            dashapp.server.view_functions[view_func] = login_required(
                dashapp.server.view_functions[view_func])


def register_extensions(server):
    from app.extensions import db
    from app.extensions import login
    from app.extensions import migrate

    db.init_app(server)
    login.init_app(server)
    login.login_view = 'main.login'  # type: ignore
    migrate.init_app(server, db)


def register_blueprints(server):
    from app.webapp import server_bp

    server.register_blueprint(server_bp)
