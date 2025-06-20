import draw_trees
import millennia_data
from flask import Flask, make_response, request

import os

app = Flask(__name__)

@app.route("/unit-upgrade-tree.svg", methods=["GET"])
def unit_upgrade_tree():
    """
    returns an SVG of the upgrade tree and relevant techs in an HTTP response.
    """
    try:
        graph = draw_trees.build_unit_upgrade_graph(request.args.get("entity"))
        graph.format = "svg"
        image = graph.pipe()
        response = make_response(image)
        response.headers.set("Content-Type", "image/svg+xml")
        return response

    except Exception as e:
        print(f"error: {e}")

        return "Internal Server Error", 500

@app.route("/improvement-upgrade-tree.svg", methods=["GET"])
def improvement_upgrade_tree():
    """
    returns an SVG of the upgrade tree and relevant techs in an HTTP response.
    """
    try:
        graph = draw_trees.build_improvement_upgrade_graph(request.args.get("entity"))
        graph.format = "svg"
        image = graph.pipe()
        response = make_response(image)
        response.headers.set("Content-Type", "image/svg+xml")
        return response

    except Exception as e:
        print(f"error: {e}")

        return "Internal Server Error", 500

@app.route("/building-upgrade-tree.svg", methods=["GET"])
def building_upgrade_tree():
    """
    returns an SVG of the upgrade tree and relevant techs in an HTTP response.
    """
    try:
        graph = draw_trees.build_building_upgrade_graph(request.args.get("entity"))
        graph.format = "svg"
        image = graph.pipe()
        response = make_response(image)
        response.headers.set("Content-Type", "image/svg+xml")
        return response

    except Exception as e:
        print(f"error: {e}")

        return "Internal Server Error", 500

@app.route("/upgrades-by-terrain.svg", methods=["GET"])
def improvements_by_terrain_tree():
    """
    returns an SVG of the upgrade tree and relevant techs in an HTTP response.
    """
    try:
        requirements = request.args.get("requirements")
        graph = draw_trees.build_terrain_upgrade_graph(requirements)
        graph.format = "svg"
        image = graph.pipe()
        response = make_response(image)
        response.headers.set("Content-Type", "image/svg+xml")
        return response

    except Exception as e:
        print(f"error: {e}")

        return "Internal Server Error", 500

@app.route("/upgrades-by-town-bonus.svg", methods=["GET"])
def improvements_by_town_bonus_tree():
    """
    returns an SVG of the upgrade tree and relevant techs in an HTTP response.
    """
    try:
        requirements = request.args.get("town")
        graph = draw_trees.build_town_bonus_upgrade_graph(requirements)
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
    returns a list of selectable entities in an HTTP response.
    """
    try:
        response = make_response(millennia_data.get_unlockable_entity_ids(millennia_data.units))
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    except Exception as e:
        print(f"error: {e}")

        return "Internal Server Error", 500

@app.route("/improvements", methods=["GET"])
def improvements():
    """
    returns a list of selectable entities in an HTTP response.
    """
    try:
        response = make_response(millennia_data.get_unlockable_entity_ids(millennia_data.improvements))
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    except Exception as e:
        print(f"error: {e}")

        return "Internal Server Error", 500
    
@app.route("/terrains", methods=["GET"])
def terrains():
    """
    returns a list of possible terrain restrictions on improvements in an HTTP response.
    """
    try:
        response = make_response(millennia_data.get_improvement_terrains())
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    except Exception as e:
        print(f"error: {e}")

        return "Internal Server Error", 500

@app.route("/buildings", methods=["GET"])
def buildings():
    """
    returns a list of selectable entities in an HTTP response.
    """
    try:
        response = make_response(millennia_data.get_unlockable_entity_ids(millennia_data.buildings))
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    except Exception as e:
        print(f"error: {e}")

        return "Internal Server Error", 500

@app.route("/town-bonuses", methods=["GET"])
def town_bonuses():
    """
    returns a list of possible town adjacency bonus types in an HTTP response.
    """
    try:
        response = make_response(millennia_data.get_town_bonuses())
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    except Exception as e:
        print(f"error: {e}")

        return "Internal Server Error", 500

# if __name__ == "__main__":
#     PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8080

#     # This is used when running locally. Gunicorn is used to run the
#     # application on Cloud Run. See entrypoint in Dockerfile.
#     app.run(host="127.0.0.1", port=PORT, debug=True)
