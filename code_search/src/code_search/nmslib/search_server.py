import os
from flask import Flask, request, abort, jsonify, make_response


class CodeSearchServer:
  """Flask server wrapping the Search Engine.

  This utility class simply wraps the search engine
  into an HTTP server based on Flask.

  Args:
    engine: An instance of CodeSearchEngine.
    host: A string host in IPv4 format.
    port: An integer for port binding.
  """
  def __init__(self, engine, host='0.0.0.0', port=8008):
    self.app = Flask(__name__,
                     static_folder=os.path.abspath(os.path.join(__file__,
                                                                '../../ui/build')),
                     static_url_path='')
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

      num_results = int(request.args.get('n', 2))
      result = self.engine.query(query_str, k=num_results)
      return make_response(jsonify(result=result))

  def run(self):
    self.app.run(host=self.host, port=self.port)
