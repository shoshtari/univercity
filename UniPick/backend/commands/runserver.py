from flask import Flask, jsonify, request
from waitress import serve
from common import configs


import logging
logger = logging.getLogger(__name__)
def create_app() -> Flask:
	app = Flask(__name__)

	@app.get("/")
	def index():
		return jsonify({"status": "ok", "service": "UniPick"})

	@app.get("/health")
	def health():
		return jsonify({"status": "healthy"})

	return app

def runserver():
	app = create_app()
	logger.info(f"Starting UniPick backend server on {configs.WEBSERVER_HOST}:{configs.WEBSERVER_PORT}")
	serve(
	 	app,
	   host=configs.WEBSERVER_HOST,
	   port=configs.WEBSERVER_PORT,
	   threads=configs.WEBSERVER_THREADS,
	   connection_limit=configs.WEBSERVER_CONNECTION_LIMIT
	)