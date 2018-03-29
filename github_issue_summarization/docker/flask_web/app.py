"""
Simple app that parses predictions from a trained model and displays them.
"""

import requests
from flask import Flask, json, render_template, request
APP = Flask(__name__)

@APP.route("/")
def index():
  """Default route.

  Placeholder, does nothing.
  """
  return render_template("index.html")

@APP.route("/summary", methods=['GET', 'POST'])
def summary():
  """Main prediction route.

  Provides a machine-generated summary of the given text. Sends a request to a live
  model trained on GitHub issues.
  """
  if request.method == 'POST':
    issue_text = request.form["issue_text"]

    url = "http://ambassador:80/seldon/issue-summarization/api/v0.1/predictions"
    headers = {'content-type': 'application/json'}
    json_data = {
      "data" : {
        "ndarray" : [[issue_text]]
      }
    }

    response = requests.post(url=url,
                             headers=headers,
                             data=json.dumps(json_data))

    response_json = json.loads(response.text)
    issue_summary = response_json["data"]["ndarray"][0][0]

    return render_template("issue_summary.html",
                           issue_text=issue_text,
                           issue_summary=issue_summary)
  return ('', 204)

if __name__ == '__main__':
  APP.run(debug=True, host='0.0.0.0', port=80)
