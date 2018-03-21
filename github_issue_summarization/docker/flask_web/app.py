"""
Simple app that parses predictions from a trained model and displays them.
"""

from flask import Flask, json, render_template, request
import requests
app = Flask(__name__)

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/summary", methods=['GET', 'POST'])
def summary():
  if request.method == 'POST':
    issue_text = request.form["issue_text"]

    url = "http://ambassador:80/seldon/issue-summarization/api/v0.1/predictions"
    headers = { 'content-type': 'application/json' }
    json_data = {
        "data" : {
          "ndarray" : [[ issue_text ]]
        }
    }

    r = requests.post(url = url,
                      headers = headers,
                      data = json.dumps(json_data))

    rjs = json.loads(r.text)
    summary = rjs["data"]["ndarray"][0][0]

    return render_template("summary.html",
                           issue_text = issue_text,
                           summary = summary)

if __name__ == '__main__':
  app.run(debug = True, host = '0.0.0.0', port = 80)

