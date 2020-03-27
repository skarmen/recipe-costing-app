"""The from app import app statement imports the app variable that is a member
of the app package."""

# app/__init__.py: Flask application instance
from .spreadsheet import (
    get_ingredients_by_category,
    add_recipe_to_sheet,
    get_existing_sheet_names,
    get_ingredients_list,
    insert_new_ingredient,
    get_final_recipe_cost,
    create_recipe_group_sheet,
    get_recipe_info,
)
from flask import (
    Flask,
    flash,
    redirect,
    url_for,
    request,
    send_from_directory,
    make_response,
)  # Flask class is impored from the flask package
from flask import render_template

# XXX FOR HTTP AUTHENTICATION
# from https://flask-httpauth.readthedocs.io/en/latest/
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from .config import Config  # Config class imported from the config.py

# from forms import SubmitForm

# XXX FIX CACHING ISSUE WITH INGREDIENT LIST ###
# from https://arusahni.net/blog/2014/03/flask-nocache.html
from flask import make_response
from functools import wraps, update_wrapper
from datetime import datetime
import os

# load the .env library that parses the .env file
# & populates the os.environ system variable
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__, static_url_path="")
app.config.from_object(Config)

auth = HTTPBasicAuth()


def nocache(view):
    # view refers to the def index() function that @nocache decorates
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Last-Modified"] = datetime.now()
        response.headers[
            "Cache-Control"
        ] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "-1"
        return response

    return update_wrapper(no_cache, view)


# from https://flask-httpauth.readthedocs.io/en/latest/
# Read the username and password from the environment variables
# TODO: how to have multiple users at once
user = os.environ.get("RECIPE_USER")
pwd = os.environ.get("RECIPE_PASSWORD")
users = {
    user: generate_password_hash(pwd),
}
# users = json.load(os.environ.get('....'))
@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False


@app.route("/")
@auth.login_required
@nocache
def index():
    # when you have multiple returns from a function & need to assigned only
    # one of them to a var => ingredients, _, = get_ingredients_by_category()
    ingredients = get_ingredients_by_category()
    existing_sheet_names = get_existing_sheet_names()
    ingredients_list = get_ingredients_list()
    yield_units = [
        "mL",
        "g",
        "each",
    ]
    recipe_units = ["mL", "gram"]
    # ingredients = {'GRAINS' : ['quinoa', 'lentils'], 'NUTS' : ['cashews']}
    # form = SubmitForm()
    return render_template(
        "submit.html",
        title="Submit",
        # form=form,
        # categories=categories,
        ingredients=ingredients,
        yield_units=yield_units,
        recipe_units=recipe_units,
        existing_sheet_names=existing_sheet_names,
        ingredients_list=ingredients_list,
    )


@app.route("/submit", methods=["POST"])
def submit():
    # get form data from request and print it with flask
    request_form = request.form  # ImmutableMultiDict
    print("request_form:", request_form)
    # convert it to regular dict (to_dict)
    request_form_dict = request_form.to_dict(flat=False)
    print("request_form_dict:", request_form_dict)
    final_recipe_cost = add_recipe_to_sheet(request_form_dict)
    recipe_name = get_recipe_info(request_form_dict)
    recipe_info = get_recipe_info(request_form_dict)
    recipe_name = recipe_info["recipe_name"]
    flash(
        f'You succefully submitted a recipe!\n'
        f'The total recipe cost for "{recipe_name}" including packaging'
        f' and labour is {final_recipe_cost}.\n'
        f' Please note this costing is pending review.'
        f' The final cost is subject to change.'
    )
    return redirect(url_for("index"))


@app.route("/submit_new_ingredient", methods=["POST", "GET"])
def submit_new_ingredient():
    # import ipdb;ipdb.set_trace()
    request_data = request.data.decode()  # ImmutableMultiDict
    print("request_data:", request_data)
    new_ingredient_input = request_data
    print("new_ingredient_input:", new_ingredient_input)
    insert_new_ingredient(new_ingredient_input)
    return ""


@app.route("/submit_new_recipe_group", methods=["POST", "GET"])
def submit_new_recipe_group():
    # import ipdb;ipdb.set_trace()
    request_data = request.data.decode()
    print("request_data:", request_data)
    new_recipe_group_input = request_data
    print("new_recipe_group_input:", new_recipe_group_input)
    create_recipe_group_sheet(new_recipe_group_input)
    return ""


@app.route("/js/<path:path>")
def send_js(path):
    return send_from_directory("static/js/", path)


@app.route("/test")
def asdfasdfasdf():
    return "test!!!"


if __name__ == "__main__":
    print("this is in recipe_portal.py __main__")
    app.run()
