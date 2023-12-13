from flask import Flask, render_template


def create_web_app(config=None):
    # Create a Flask instance and configure it to use relative paths
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='development',  # TODO: Change to UUID when finalizing
        static_url_path='',
        static_folder='static',
        template_folder='templates'
    )

    if config is None:
        # Use the above configuration if none is provided
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Use the provided configuration
        app.config.from_mapping(config)

    @app.route('/')
    def main():
        return render_template('grouper.html')

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app


app = create_web_app()
