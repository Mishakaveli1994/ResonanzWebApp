import os

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from utils.reader import pandas_reader, polars_reader

def create_web_app(config=None):
    # Create a Flask instance and configure it to use relative paths

    app = Flask(__name__, instance_relative_config=True)
    UPLOAD_FOLDER = app.root_path + 'static/files'
    ALLOWED_EXTENSIONS = {'csv'}  # TODO: Check file format
    # TODO: Check size of uploaded files
    app.config.from_mapping(
        SECRET_KEY='development',  # TODO: Change to UUID when finalizing
        static_url_path='',
        static_folder='static',
        template_folder='templates',
        UPLOAD_FOLDER=UPLOAD_FOLDER,
    )

    if config is None:
        # Use the above configuration if none is provided
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Use the provided configuration
        app.config.from_mapping(config)

    @app.route('/', methods=['GET', 'POST'])
    def main():
        if request.method == 'POST':
            print(request.form['input-area'])
            if request.files['address-csv']:
                file = request.files['address-csv']
                #pandas_reader(file.stream)
                polars_reader(file.stream)
                # print(file.read())
                # for i in file.stream:
                #     print(i.decode('utf-8'))

                # read_csv(file.read())
                # fn = secure_filename(file.filename) # TODO: Remove if unneeded
                # file.save(os.path.join(app.config['UPLOAD_FOLDER'], fn)) # TODO: Remove if unneeded
        return render_template('grouper.html')

    @app.route('/about', methods=['GET'])
    def about():
        return render_template('about.html')

    @app.errorhandler(404)  # TODO: Implement 404
    def page_not_found(e):
        return render_template('404.html')

    return app


# TODO: Animation while loading output. Test with delay
# TODO: Toggle between send file and send via text
# TODO: Implement file loop, pandas and polars
# TODO: Create a switch in HTML that the different modes can be toggled
# TODO: Display the time it took the commands to complete to compare performance
# TODO: Create decorator for timing
# TODO: Add function descriptions and types

app = create_web_app()
