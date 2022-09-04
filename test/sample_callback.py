from urllib import request
from flask import Flask
from flask import request

app = Flask(__name__)

@app.route("/sample_callback", methods=["POST"])
def test():
    """
    """
    print(request.json)

    return "", 200

if __name__ == "__main__":
    app.logger.info("Running on un-secure port: %s" % 14000)
    app.run(host="127.0.0.1", port="14000")