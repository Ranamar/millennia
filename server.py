from draw_trees import build_unit_upgrade_graph
import millennia_data
from flask import Flask, make_response, request

import os

app = Flask(__name__)

@app.route("/upgrade_tree.svg", methods=["GET"])
def upgrade_tree():
    """
    returns an SVG of the upgrade tree and relevant techs in an HTTP response.
    """
    try:
        graph = build_unit_upgrade_graph(request.args.get("entity"))
        graph.format = "svg"
        image = graph.pipe()
        response = make_response(image)
        response.headers.set("Content-Type", "image/svg+xml")
        return response

    except Exception as e:
        print(f"error: {e}")

        return "Internal Server Error", 500


@app.route("/units", methods=["GET"])
def units():
    """
    returns an SVG of the upgrade tree and relevant techs in an HTTP response.
    """
    try:
        response = make_response(sorted(millennia_data.units.keys()))
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    except Exception as e:
        print(f"error: {e}")

        return "Internal Server Error", 500


if __name__ == "__main__":
    PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8080

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host="127.0.0.1", port=PORT, debug=True)
