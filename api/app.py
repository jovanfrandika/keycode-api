from flask import Flask, request, json
from werkzeug.exceptions import HTTPException

from requests.auth import HTTPBasicAuth
import requests

import os
import base64
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

baseURL = "https://api.github.com"
auth = HTTPBasicAuth(os.getenv('GITHUB_CLIENT_ID'),
                     os.getenv('GITHUB_CLIENT_SECRET'))


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


@app.route("/")
def home():
    return "<h1>Keycodes API</h1>"


@app.route("/file")
def download_file():
    url = request.args.get("url")
    try:
        github_file = requests.get(url, auth=auth)
        content = github_file.json()["content"]
        decode = base64.b64decode(content)
        return decode
    except Exception as e:
        return handle_exception(e)


@app.route("/tree")
def search_trees(treeUrl=""):
    url = request.args.get("url")
    try:
        if url:
            tree_search = requests.get(url, auth=auth)
        else:
            tree_search = requests.get(treeUrl, auth=auth)
        return tree_search.json()
    except Exception as e:
        return handle_exception(e)


@app.route("/search/repo")
def search_repositories():
    try:
        query = request.args.get("q")
        search = requests.get(
            f"{baseURL}/search/repositories?q={query}&sort=stars&order=desc", auth=auth)
        return search.json()
    except Exception as e:
        return handle_exception(e)


@ app.route("/search/files")
def search_files():
    try:
        repo = request.args.get("repo")
        owner = request.args.get("owner")

        # 1. Get latest commit SHA
        # GET /repos/:owner/:repo/commits
        commit_search = requests.get(
            f"{baseURL}/repos/{owner}/{repo}/commits", auth=auth)
        latest_commit_sha = commit_search.json()[0]["sha"]

        # 2. Use the latest commit SHA to get the tree SHA
        # GET /repos/:owner/:repo/git/commits/:sha
        tree_search = requests.get(
            f"{baseURL}/repos/{owner}/{repo}/git/commits/{latest_commit_sha}", auth=auth)
        tree_sha = tree_search.json()["tree"]["sha"]
        tree_url = tree_search.json()["tree"]["url"]

        # 3. Use the tree URL to get the file structure
        # GET /repos/:owner/:repo/git/trees/:sha
        return search_trees(tree_url)
    except Exception as e:
        return handle_exception(e)


if __name__ == "__main__":
    app.run(port=4000, debug=True)
