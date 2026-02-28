from api2 import create_app


# Entrypoint module for the Flask-based API 2.0.
app = create_app()


if __name__ == '__main__':
    # Local development server; production should use gunicorn.
    app.run(debug=False)
    