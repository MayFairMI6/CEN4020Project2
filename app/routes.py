import os
from flask import Blueprint, request, jsonify, render_template
from .excel_service import import_excel
from .export_service import export_schedule


main_routes = Blueprint("main", __name__)

@main_routes.route("/")
def home():
    return render_template("home.html")

@main_routes.route("/upload", methods = ["POST"])
def upload():
    file = request.files.get("file")
    if file is None:
        return jsonify({"message": "Missing file field."}), 400

    try:
        result = import_excel(file)
        return jsonify(result)
    except ValueError as exc:
        return jsonify({"message": str(exc)}), 400

@main_routes.route("/export/schedule/<format>")
def export(format):
    return export_schedule(format)