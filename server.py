try:
    # try to import flask, or return error if has not been installed
    from flask import Flask
    from flask import send_from_directory
except ImportError:
    print("You don't have Flask installed, run `$ pip3 install flask` and try again")
    exit(1)

import os, subprocess

static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), './')
app = Flask(__name__)


@app.after_request
def apply_cache_policy(response):
    """Apply cache headers that are bfcache-friendly."""
    content_type = response.headers.get("Content-Type", "")

    if content_type.startswith("text/html"):
        # Keep HTML short-lived but cacheable; avoid no-store/no-cache.
        response.cache_control.public = True
        response.cache_control.max_age = 60
        response.cache_control.no_cache = False
        response.cache_control.no_store = False
        response.headers["X-Robots-Tag"] = "index, follow"
        response.headers.pop("Pragma", None)
    else:
        # Static assets can be cached longer.
        response.cache_control.public = True
        response.cache_control.max_age = 3600
        response.cache_control.no_cache = False
        response.cache_control.no_store = False

    return response

# Serving the index file
@app.route('/', methods=['GET'])
def serve_dir_directory_index():
    if os.path.exists("app.py"):
        # if app.py exists we use the render function
        out = subprocess.Popen(['python3','app.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout,stderr = out.communicate()
        return stdout if out.returncode == 0 else f"<pre style='color: red;'>{stdout.decode('utf-8')}</pre>"
    if os.path.exists("index.html"):
        return send_from_directory(static_file_dir, 'index.html')
    else:
        return "<h1 align='center'>404</h1><h2 align='center'>Missing index.html file</h2><p align='center'><img src='https://github.com/4GeeksAcademy/html-hello/blob/main/.vscode/rigo-baby.jpeg?raw=true' /></p>"

# Serving any other image
@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = os.path.join(path, 'index.html')
    return send_from_directory(static_file_dir, path)

app.run(host='0.0.0.0',port=3000, debug=True, extra_files=['./',])
