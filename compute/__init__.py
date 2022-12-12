from flask import Flask


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        MYSQL_HOST='localhost',
        MYSQL_PORT=3306,
        MYSQL_USER='root',
        MYSQL_PASSWORD='root',
        MYSQL_DATABASE='test',
        RABBITMQ_HOST='localhost',
        RABBITMQ_PORT=5672
    )

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from .exec import exec_blueprint
    app.register_blueprint(exec_blueprint, url_prefix='/exec')


    return app
