'''API getting books photo used for line'''

from flask import Blueprint, request, send_file

image_bp = Blueprint("image_bp", __name__)

@image_bp.route("/images", methods=["GET"])
def get_image():

    file_name = request.args.get("file_name")
    print(file_name)
    return send_file(f"static/book/{file_name}", mimetype = "image/jpeg")