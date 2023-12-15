from flask import Flask, render_template, request, jsonify
import io
from .utils.reader import processors


def create_web_app(config=None):
    # Create a Flask instance and configure it to use relative paths

    app = Flask(__name__, instance_relative_config=True)
    # TODO: Check size of uploaded files
    app.config.from_mapping(
        SECRET_KEY='development',  # TODO: Change to UUID when finalizing
        static_url_path='',
        static_folder='static',
        template_folder='templates',
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
            processor_switch = 'pandas-df' if request.form.get('processor') == 'pandas' else 'polars-df'
            processor = processors[processor_switch]
            print(f"{processor.__name__} selected")
            if request.files['address-csv']:
                file = request.files['address-csv']
                output = processor(file)
            else:
                output = processor(io.StringIO(f"{request.form.get('input-area')}"))
            print(output)
            return jsonify({'output': output})
        else:
            return render_template('grouper.html')

    @app.route('/about', methods=['GET'])
    def about():
        return render_template('about.html')

    @app.errorhandler(404)  # TODO: Implement 404
    def page_not_found(e):
        return render_template('404.html')

    return app


# TODO: Animation while loading output. Test with delay
# TODO: Display the time it took the commands to complete to compare performance
# TODO: Add function descriptions and types
# TODO: Trim before and after spaces
# TODO: Display error if no input or input at both fields
# TODO: Refresh inputs on send
# TODO: Check if CSV is valid
app = create_web_app()
