import os

# TODO: use env vars for all of these
DATABASE_URL = "sqlite:////tmp/unipick.db"
WEBSERVER_HOST = "0.0.0.0"
WEBSERVER_PORT = 8000
WEBSERVER_THREADS = 40
WEBSERVER_CONNECTION_LIMIT = 100

JWT_ENCRYPT_KEY = os.environ.get(
    "JWT_ENCRYPT_KEY", "a" * 32
)  # in order for tests to run ok, #TODO: add reevaluate environ func and handle tests by setting env var in test setup
JWT_DECRYPT_KEY = os.environ.get("JWT_DECRYPT_KEY", JWT_ENCRYPT_KEY)
JWT_ALGORITHM = "HS256"
JWT_TTL = 900

BCRYPT_ROUNDS = 12

PDF_ENGINE = "pdfplumber"  # either "camelot" or "pdfplumber"

RUN_HEAVY_TESTS = False
WSGI_SERVER = "waitress"  #  either "waitress" or "flask" use flask only for development

CORS_ORIGIN ="http://localhost:5173"
