#!/usr/bin/env python3
from flask import Flask, render_template, request, url_for, redirect
from flask import make_response
from flask import Flask, session as login_session
from flask_httpauth import HTTPTokenAuth
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from itsdangerous import TimedJSONWebSignatureSerializer as JWT
from itsdangerous import BadSignature, SignatureExpired
import random
import string
from oauth2client import client, file
import httplib2
from googleapiclient.discovery import build
import json
from database_setup import Base, User, Category, LearningItem, Resource
from ui_classes import ItemUI

app = Flask(__name__)
app.secret_key = "VPMBN89DO7OFWG82LBWPZ6072Y9U7082"
#file = open("/var/www/ItemCatalog/json/client_secrets.json", "r").read()
#CLIENT_ID = json.loads(file)["web"]["client_id"]
auth = HTTPTokenAuth(scheme="Bearer")
# secret_key for API token generation
# validity one hour
# "".join(random.choice(string.ascii_uppercase + string.digits)
#   for x in range(32))
secret_key = "3K78ONCNMYYNGSSFKZMIA1T76Y99WTT6"
VALIDITY = 3600
jwt = JWT(secret_key, expires_in=VALIDITY)

engine = create_engine("postgresql://catalog:catalog@localhost/tolearn")
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# User authentication
@app.route("/")
def show_login():
    # generate CSRF token and store it in user session cookie
    state = (
        "".join(random.choice(string.ascii_uppercase +
                              string.digits) for x in range(32))
    )
    login_session["state"] = state
    # make it accessible by javascript in template
    if "access_token" not in login_session:
        return render_template("login.html", STATE=state)
    else:
        return redirect("/cat/", code=302)


@app.route("/gconnect", methods=["POST"])
def gconnect():
    if request.args.get("state") != login_session["state"]:
        response = make_response(json.dumps({"error": "Invalid state"}), 401)
        response.headers["Content-Type"] = "application/json"
        return response
    code = request.data
    try:
        flow = client.flow_from_clientsecrets(
            "/var/www/ItemCatalog/json/client_secrets.json",
            scope=["email"],
            redirect_uri="postmessage")
        credentials = flow.step2_exchange(code)
    except Exception as e:
        response = make_response(json.dumps({"error": str(e)}), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    login_session["access_token"] = credentials.access_token
    login_session["gplus_id"] = credentials.id_token["sub"]
    login_session["email"] = credentials.id_token["email"]
    # additional user infos can be requested with
    # people.get endpoint (userinfo endpoint is deprecated!)
    http_auth = credentials.authorize(httplib2.Http())
    service = build('plus', 'v1', credentials=credentials)
    user_info = service.people().get(userId="me").execute()
    login_session["username"] = user_info["displayName"]
    # if user does not exist, create user
    try:
        user_id = get_user_id(login_session["email"])
    except Exception as e:
        create_user(name=login_session["username"],
                    email=login_session["email"])
        session.commit()
        user_id = get_user_id(login_session["email"])
    login_session["user_id"] = user_id
    return redirect("/cat/", code=302)


@app.route("/gdisconnect")
def gdisconnect():
    if "access_token" not in login_session:
        response = make_response(json.dumps({"error": "Not logged in"}), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    # credentials object couldn't be stored in session
    # --> credentials.revoke(httplib2.Http()) cannot be used
    # instead use HTTP/REST
    at = login_session["access_token"]
    url = (
        "https://accounts.google.com/o/oauth2/revoke?token={at}"
        .format(at=at)
        )
    h = httplib2.Http()
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    resp, content = h.request(url, "GET", headers=headers)

    # no need to check response status
    # if token expired, ignore it as we don't need it anymore anyway
    # delete session data
    del login_session["access_token"]
    del login_session["gplus_id"]
    del login_session["username"]
    del login_session["email"]

    response = make_response(json.dumps({"info": "Disconnected"}), 200)
    response.headers["Content-Type"] = "application/json"
    return response


# CRUD Category
@app.route("/cat/create/", methods=["POST"])
def create_cat():
    user_id = login_session["user_id"]
    if user_id is not None:
        data = request.get_json()

        try:
            new_cat = Category(user_id=user_id, name=data["newName"])
            session.add(new_cat)
            session.commit()
        except Exception as e:
            session.rollback()
            response = make_response(
                json.dumps({"error": "Creation failed"}), 400)
            response.headers["Content-Type"] = "application/json"
            return response

        response = make_response(
            json.dumps({"info": "Category created"}), 200)
        response.headers["Content-Type"] = "application/json"
        return response
    else:
        response = make_response(
            json.dumps({"error": "No permission"}), 401)
        response.headers["Content-Type"] = "application/json"
        return response


@app.route("/cat/")
def show_cat():
    try:
        username = login_session["username"]
        user_id = login_session["user_id"]
        categories = get_user_categories(user_id=user_id)
    except Exception as e:
        response = make_response(
            json.dumps({"error": "Could not read categories"}), 400)
        response.headers["Content-Type"] = "application/json"
        return response
    return render_template("cat.html",
                           name=username,
                           categories=categories)


@app.route("/cat/<int:category_id>/edit/", methods=["POST"])
def edit_cat(category_id):
    user_id = login_session["user_id"]
    if user_is_allowed(user_id=user_id, category_id=category_id):
        try:
            data = request.get_json()
            cat = session.query(Category).filter_by(id=category_id).one()
            cat.name = data["newName"]
            session.add(cat)
            session.commit()
            response = make_response(
                json.dumps({"info": "Category renamed"}),
                200)
            response.headers["Content-Type"] = "application/json"
            return response
        except Exception as e:
            session.rollback()
            response = make_response(
                json.dumps({"error": "Rename failed"}),
                400)
            response.headers["Content-Type"] = "application/json"
            return response
    else:
        response = make_response(json.dumps({"error": "No permission"}), 401)
        response.headers["Content-Type"] = "application/json"
        return response


@app.route("/cat/<int:category_id>/delete/", methods=["POST"])
def del_cat(category_id):
    user_id = login_session["user_id"]
    if user_is_allowed(user_id=user_id, category_id=category_id):
        try:
            cat = session.query(Category).filter_by(id=category_id).one()
            if (
                session.query(LearningItem)
                .filter_by(category_id=category_id).first() is None
            ):
                # only delete category if no items are left
                session.delete(cat)
                session.commit()
                response = make_response(
                    json.dumps({"info": "Category deleted"}),
                    200)
                response.headers["Content-Type"] = "application/json"
                return response
            else:
                response = make_response(
                    json.dumps({"error": "Please delete items first"}),
                    400)
                response.headers["Content-Type"] = "application/json"
                return response
        except Exception as e:
            session.rollback()
            response = make_response(
                json.dumps({"error": "Deletion failed"}),
                400)
            response.headers["Content-Type"] = "application/json"
            return response
    else:
        response = make_response(json.dumps({"error": "No permission"}),
                                 401)
        response.headers["Content-Type"] = "application/json"
        return response


# CRUD Item
@app.route("/cat/<int:category_id>/item/create/", methods=["GET", "POST"])
def create_item(category_id):
    user_id = login_session["user_id"]
    if user_is_allowed(user_id=user_id, category_id=category_id):
        if request.method == "POST":
            try:
                create_item_from_request(request, category_id)
                session.commit()
                response = make_response(
                    json.dumps({"info": "Item created!"}),
                    200)
                response.headers["Content-Type"] = "application/json"
                return response
            except Exception as e:
                session.rollback()
                response = make_response(
                    json.dumps({"error": "Creation failed"}),
                    400)
                response.headers["Content-Type"] = "application/json"
                return response
        else:
            # GET method
            username = login_session["username"]
            cat = session.query(Category).filter_by(id=category_id).one()
            return render_template(
                "create_item.html",
                name=username,
                category=cat
            )
    else:
        response = make_response(json.dumps({"error": "No permission"}), 401)
        response.headers["Content-Type"] = "application/json"
        return response


@app.route("/cat/<int:category_id>/item/")
def show_items_in_cat(category_id):
    user_id = login_session["user_id"]
    if user_is_allowed(user_id=user_id, category_id=category_id):
        try:
            username = login_session["username"]
            cat = session.query(Category).filter_by(id=category_id).one()
            # show the items of first user category when logging in
            items = get_items_in_category(category_id)
            items_ui = map_to_ui_obj(items)
            return render_template("item.html",
                                   name=username,
                                   category=cat,
                                   items=items_ui)
        except Exception as e:
            response = make_response(
                json.dumps({"error": "Could not read items"}),
                400)
            response.headers["Content-Type"] = "application/json"
            return response
    else:
        response = make_response(json.dumps({"error": "No permission"}), 401)
        response.headers["Content-Type"] = "application/json"
        return response


@app.route("/cat/<int:category_id>/item/<int:item_id>/edit/",
           methods=["GET", "POST"])
def edit_item(category_id, item_id):
    user_id = login_session["user_id"]
    if (
        user_is_allowed(user_id=user_id, category_id=category_id) and
        item_belongs_to_category(category_id=category_id, item_id=item_id)
    ):
        if request.method == "POST":
            try:
                update_item_from_request(request, category_id, item_id)
                session.commit()
                response = make_response(
                    json.dumps({"error": "Edit successful!"}),
                    200)
                response.headers["Content-Type"] = "application/json"
                return response
            except Exception as e:
                session.rollback()
                response = make_response(
                    json.dumps({"error": "Could not update item"}),
                    400)
                response.headers["Content-Type"] = "application/json"
                return response
        else:
            # GET method
            username = login_session["username"]
            category = session.query(Category).filter_by(id=category_id).one()
            item = session.query(LearningItem).filter_by(id=item_id)
            item_ui = map_to_ui_obj(item)[0]
            return render_template(
                "edit_item.html",
                name=username,
                category=category,
                item=item_ui
            )
    else:
        response = make_response(json.dumps({"error": "No permission"}), 401)
        response.headers["Content-Type"] = "application/json"
        return response


@app.route("/cat/<int:category_id>/item/<int:item_id>/delete/",
           methods=["POST"])
def del_item(category_id, item_id):
    user_id = get_user_id(login_session["email"])
    if (
        user_is_allowed(user_id=user_id, category_id=category_id) and
        item_belongs_to_category(category_id, item_id)
    ):
        try:
            resource = session.query(Resource).filter_by(item_id=item_id)
            for r in resource:
                session.delete(r)
            item = session.query(LearningItem).filter_by(id=item_id).one()
            session.delete(item)
            session.commit()
            response = make_response(
                json.dumps({"info": "Item and resources deleted"}),
                200)
            response.headers["Content-Type"] = "application/json"
            return response
        except Exception as e:
            session.rollback()
            response = make_response(json.dumps({"error": "Deletion failed"}),
                                     400)
            response.headers["Content-Type"] = "application/json"
            return response
    else:
        response = make_response(json.dumps({"error": "No permission"}), 401)
        response.headers["Content-Type"] = "application/json"
        return response


#####################################
# JSON endpoints
#####################################
# test page for endpoints, no productive use
@app.route("/testapi/")
def test():
    return render_template("test_api.html")


@app.route("/api/token/")
def get_auth_token():
    # user needs to request token first to send with API request
    if "user_id" not in login_session:
        response = make_response(json.dumps({"error": "No permission"}), 401)
        response.headers["Content-Type"] = "application/json"
        return response
    else:
        user_id = login_session["user_id"]
        user = session.query(User).filter_by(id=user_id).one()
        token = generate_auth_token(user_id)
    response = make_response(json.dumps({"token": token.decode("ascii"),
                                        "validity": VALIDITY}), 200)
    response.headers["Content-Type"] = "application/json"
    return response


# verify token
def generate_auth_token(user_id):
    token = jwt.dumps({"id": user_id})
    return token


def verify_auth_token(token):
    try:
        data = jwt.loads(token)
    except SignatureExpired as e:
        # Valid token, but expired
        return None
    except BadSignature as e:
        # Invalid token
        return None
    user_id = data["id"]
    return user_id


@auth.verify_token
def verify_token(token):
    user_id = verify_auth_token(token)
    if user_id:
        return True
    return False


# JSON endpoint: Get all categories
@app.route("/api/cat/")
@auth.login_required
def get_json_api_cat():
    header = request.headers
    token = header["Authorization"]
    token = token[7:]
    # get token --> parse user
    user_id = verify_auth_token(token)
    cat = session.query(Category).filter_by(user_id=user_id).all()
    cat_list = []
    for c in cat:
        cat_dict = {
            "id": c.id,
            "name": c.name
        }
        cat_list.append(cat_dict.copy())
    response = make_response(json.dumps(cat_list), 200)
    response.headers["Content-Type"] = "application/json"
    return response


# JSON endpoint: Get all items of category
@app.route("/api/cat/<int:category_id>/item/")
@auth.login_required
def get_json_api_cat_items(category_id):
    header = request.headers
    token = header["Authorization"]
    token = token[7:]
    # get token --> parse user
    user_id = verify_auth_token(token)
    try:
        if user_is_allowed(user_id=user_id, category_id=category_id):
            items = (
                session.query(LearningItem)
                .filter_by(category_id=category_id)
                .all()
            )
            item_list = []
            for i in items:
                resources = (
                    session.query(Resource)
                    .filter_by(item_id=i.id)
                    .all()
                )
                rsrc_list = []
                for r in resources:
                    rsrc_dict = {
                        "name": r.name,
                        "url": r.url
                    }
                    rsrc_list.append(rsrc_dict.copy())
                item_dict = {
                    "id": i.id,
                    "name": i.name,
                    "desc": i.description,
                    "done": i.done,
                    "resources": rsrc_list
                }
                item_list.append(item_dict.copy())
            response = make_response(json.dumps(item_list), 200)
            response.headers["Content-Type"] = "application/json"
            return response
        else:
            response = make_response(json.dumps({"error": "No permission"}),
                                     401)
            response.headers["Content-Type"] = "application/json"
            return response
    except Exception as e:
        response = make_response(json.dumps({"error": str(e)}), 400)
        response.headers["Content-Type"] = "application/json"
        return response


# JSON endpoint: Get item
@app.route("/api/cat/<int:category_id>/item/<int:item_id>/")
@auth.login_required
def get_json_api_item(category_id, item_id):
    header = request.headers
    token = header["Authorization"]
    token = token[7:]
    # get token --> parse user
    user_id = verify_auth_token(token)
    try:
        if (user_is_allowed(user_id=user_id, category_id=category_id) and
            item_belongs_to_category(category_id=category_id,
                                     item_id=item_id)):
            print("works ok")
            item = session.query(LearningItem).filter_by(id=item_id).one()
            resources = (
                session.query(Resource)
                .filter_by(item_id=item.id)
                .all()
                )
            rsrc_list = []
            for r in resources:
                rsrc_dict = {
                    "name": r.name,
                    "url": r.url
                }
                rsrc_list.append(rsrc_dict.copy())
            item_dict = {
                "id": item.id,
                "name": item.name,
                "desc": item.description,
                "done": item.done,
                "resources": rsrc_list
            }
            response = make_response(json.dumps(item_dict), 200)
            response.headers["Content-Type"] = "application/json"
            return response
        else:
            response = make_response(json.dumps({"error": "No permission"}),
                                     401)
            response.headers["Content-Type"] = "application/json"
            return response
    except Exception as e:
        response = make_response(json.dumps({"error": str(e)}), 400)
        response.headers["Content-Type"] = "application/json"
        return response


#######################
# Helper methods
#######################
def create_user(name, email):
    newUser = User(name=name, email=email)
    session.add(newUser)


def map_to_ui_obj(items):
    items_ui = []
    for i in items:
        item_ui = ItemUI(i)
        item_ui.set_resources(get_resources_for_item(i.id))
        items_ui.append(item_ui)
    return items_ui


def get_user_categories(user_id):
    return session.query(Category).filter_by(user_id=user_id).all()


def get_items_in_category(category_id):
    return session.query(LearningItem).filter_by(category_id=category_id).all()


def get_resources_for_item(item_id):
    return session.query(Resource).filter_by(item_id=item_id).all()


def user_is_allowed(user_id, category_id):
    result = (
        session.query(Category)
        .filter_by(user_id=user_id, id=category_id)
        .one_or_none()
        )
    if result is not None:
        return True
    else:
        return False


def get_user_id(email):
    user_id = session.query(User).filter_by(email=email).one().id
    return user_id


def item_belongs_to_category(category_id, item_id):
    result = (
        session.query(LearningItem)
        .filter_by(id=item_id, category_id=category_id)
        .one_or_none()
        )
    if result is not None:
        return True
    else:
        return False


def create_item_from_request(request, category_id):
    data = request.get_json()
    # read data and create new item
    item = LearningItem(category_id=category_id,
                        name=data["name"],
                        description=data["descr"],
                        done=data["done"])
    session.add(item)
    # flush to get auto-incremented item id
    session.flush()
    # create resources
    for r in data["rsrc"]:
        rsrc = Resource(item_id=item.id,
                        name=r["name"],
                        url=r["url"])
        session.add(rsrc)


def update_item_from_request(request, category_id, item_id):
        item_data_changed = False
        rsrc_data_changed = False
        data = request.get_json()
        item = session.query(LearningItem).filter_by(id=item_id).one()
        if data["name"] != item.name:
            item.name = data["name"]
            item_data_changed = True
        if data["done"] != item.done:
            item.done = data["done"]
            item_data_changed = True
        if data["descr"] != item.description:
            item.description = data["descr"]
            item_data_changed = True
        if item_data_changed:
            session.add(item)
        # delete existing resources
        if len(data["delRsrc"]) > 0:
            for r_id in data["delRsrc"]:
                del_rsrc = (
                    session.query(Resource)
                    .filter_by(id=r_id, item_id=item_id)
                    .one()
                    )
                session.delete(del_rsrc)
        # update existing resources
        for r in data["rsrc"]:
            if "id" in r:
                rsrc = session.query(Resource).filter_by(id=r["id"]).one()
                if r["newName"] != rsrc.name:
                    rsrc.name = r["newName"]
                    rsrc_data_changed = True
                if r["newURL"] != rsrc.url:
                    rsrc.url = r["newURL"]
                    rsrc_data_changed = True
                if rsrc_data_changed:
                    session.add(rsrc)
            else:
                # add new resource
                rsrc = Resource(item_id=item_id,
                                name=r["newName"],
                                url=r["newURL"])
                session.add(rsrc)

if __name__ == "__main__":
    # key needed to sign session cookies
    #app.secret_key = "VPMBN89DO7OFWG82LBWPZ6072Y9U7082"
    app.debug = True
    app.run(host="0.0.0.0", port=8080)
