from flask import Flask, render_template, request, jsonify
import io
from .utils.reader import processors
import logging
import uuid

logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Set the format of log messages
    datefmt='%Y-%m-%d %H:%M:%S',  # Set the date format
)

logger = logging.getLogger('basic')

# Set urllib logging to WARNING so it only display messages on error'
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('werkzeug').setLevel(logging.WARNING)


def create_web_app(config=None):
    # Create a Flask instance and configure it to use relative paths

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=str(uuid.uuid4()),
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
        """
        Main route. Handles both GET and POST requests.
        """
        if request.method == 'POST':
            processor = processors[request.form.get('processor')]
            logger.info(f"Processor {processor.__name__} selected")
            if request.files['address-csv']:
                file = request.files['address-csv']
                output = processor(file)
            else:
                output = processor(io.StringIO(f"{request.form.get('input-area')}"))
            return jsonify(output)
        else:
            return render_template('neighbor_net.html')

    @app.route('/about', methods=['GET'])
    def about():
        """
        About route - creator and purpose of project page
        :return:
        """
        return render_template('about.html')

    @app.errorhandler(404)
    def page_not_found(e):
        """
        404 error handler. Self-explanatory :)
        :param e: error object (if any)
        :return:
        """
        return render_template('404.html')

    return app


app = create_web_app()
