from api2 import create_app
from api2.debug import get_logger


# Entrypoint module for the Flask-based API 2.0.
app = create_app()
logger = get_logger("api")


if __name__ == '__main__':
    # Local development server; production should use gunicorn.
    logger.info("Starting Flask development server")
    app.run(debug=False)
    