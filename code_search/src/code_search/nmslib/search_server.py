from flask import Flask, request, abort, jsonify, make_response
from flask_cors import CORS


class CodeSearchServer:
  """This utility class wraps the search engine into
  an HTTP server based on Flask"""
  def __init__(self, engine, host='0.0.0.0', port=8008):
    self.app = Flask(__name__)
    self.host = host
    self.port = port
    self.engine = engine

    self.init_routes()

  def init_routes(self):
    # pylint: disable=unused-variable

    @self.app.route('/ping')
    def ping():
      return make_response(jsonify(status=200), 200)

    @self.app.route('/query')
    def query():
      query_str = request.args.get('q')
      if not query_str:
        abort(make_response(
          jsonify(status=400, error="empty query"), 400))

      result = self.engine.query(query_str)
      return make_response(jsonify(result=result))

    @self.app.route('/embed')
    def embed():
      query_str = request.args.get('q')
      if not query_str:
        abort(make_response(
          jsonify(status=400, error="empty query"), 400))

      result = self.engine.embed(query_str)
      return make_response(jsonify(result=result))

  def run(self):
    CORS(self.app)
    self.app.run(host=self.host, port=self.port)
