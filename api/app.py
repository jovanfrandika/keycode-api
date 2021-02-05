from flask import Flask, request

from requests.auth import HTTPBasicAuth
import requests

import os
import base64
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

baseURL = "https://api.github.com"


@app.route("/")
def home():
    return "<h1>Keycodes API</h1>"


@app.route("/file")
def download_file():
    url = request.args.get("url")
    github_file = requests.get(url,
                               auth=HTTPBasicAuth(os.getenv('GITHUB_CLIENT_ID'), os.getenv('GITHUB_CLIENT_SECRET')))
    # github_file = requests.get(f"{baseURL}/repos/repositories?q={query}&sort=stars&order=desc",
    #   auth=HTTPBasicAuth(os.getenv('GITHUB_CLIENT_ID'), os.getenv('GITHUB_CLIENT_SECRET')))
    content = github_file.json()["content"]
    decode = base64.b64decode(content)
    return decode


@app.route("/tree")
def search_trees(treeUrl=""):
    url = request.args.get("url")
    if url:
        tree_search = requests.get(url,
                                   auth=HTTPBasicAuth(os.getenv('GITHUB_CLIENT_ID'), os.getenv('GITHUB_CLIENT_SECRET')))
    else:
        tree_search = requests.get(treeUrl,
                                   auth=HTTPBasicAuth(os.getenv('GITHUB_CLIENT_ID'), os.getenv('GITHUB_CLIENT_SECRET')))
    return tree_search.json()


@app.route("/search/repo")
def search_repositories():
    query = request.args.get("q")
    search = requests.get(f"{baseURL}/search/repositories?q={query}&sort=stars&order=desc",
                          auth=HTTPBasicAuth(os.getenv('GITHUB_CLIENT_ID'), os.getenv('GITHUB_CLIENT_SECRET')))
    return search.json()


@ app.route("/search/files")
def search_files():
    repo = request.args.get("repo")
    owner = request.args.get("owner")

    # 1. Get latest commit SHA
    # GET /repos/:owner/:repo/commits
    commit_search = requests.get(f"{baseURL}/repos/{owner}/{repo}/commits",
                                 auth=HTTPBasicAuth(os.getenv('GITHUB_CLIENT_ID'), os.getenv('GITHUB_CLIENT_SECRET')))
    latest_commit_sha = commit_search.json()[0]["sha"]

    # 2. Use the latest commit SHA to get the tree SHA
    # GET /repos/:owner/:repo/git/commits/:sha
    tree_search = requests.get(f"{baseURL}/repos/{owner}/{repo}/git/commits/{latest_commit_sha}",
                               auth=HTTPBasicAuth(os.getenv('GITHUB_CLIENT_ID'), os.getenv('GITHUB_CLIENT_SECRET')))
    tree_sha = tree_search.json()["tree"]["sha"]
    tree_url = tree_search.json()["tree"]["url"]

    # 3. Use the tree URL to get the file structure
    # GET /repos/:owner/:repo/git/trees/:sha
    # tree_search = requests.get(tree_url,
    #                            # tree_search = requests.get(f"{baseURL}/repos/{owner}/{repo}/git/trees/{tree_sha}",
    #                            auth=HTTPBasicAuth(os.getenv('GITHUB_CLIENT_ID'), os.getenv('GITHUB_CLIENT_SECRET')))
    # return tree_search.json()
    return search_trees(tree_url)


if __name__ == "__main__":
    app.run(port=4000, debug=True)
