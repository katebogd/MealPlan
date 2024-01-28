import os
import datetime
import pytz

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, create_url, is_ingredient_in_list, float_to_string

# Configure application
app = Flask(__name__)
app.config["SESSION_FILE_DIR"] = "/www_data/"

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///recipes.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    user_plans = db.execute("SELECT * FROM plans WHERE user_id = ? LIMIT 3", session["user_id"])
    plans = []
    for row in user_plans:
        plan = {}
        plan["name"] = row["name"]
        plan["days"] = int(row["days"])
        plan["people"] = int(row["people"])
        plan["url"] = row["url"]
        plans.append(plan)

    user_recipes = db.execute("SELECT * FROM recipes WHERE user_id = ? LIMIT 3", session["user_id"])
    recipes = []
    for row in user_recipes:
        recipe = {}
        recipe["name"] = row["name"]
        recipe["servings"] = int(row["servings"])
        recipe["time"] = row["time"]
        recipe["image"] = row["image"]
        recipe["url"] = row["url"]
        recipes.append(recipe)
    return render_template("index.html", plans=plans, recipes=recipes)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure username is unique
        elif (
            len(
                db.execute(
                    "SELECT * FROM users WHERE username = ?",
                      request.form.get("username")
                )
            )
            != 0
        ):
            return apology("must provide unique username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password was submitted the second time
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password must match confirmation", 400)

        # Add user to database
        username = request.form.get("username")
        passhash = generate_password_hash(
            request.form.get("password"), method="pbkdf2", salt_length=16
        )
        db.execute(
            "INSERT INTO users (username,hash) VALUES (?, ?)", username, passhash
        )

        # Redirect user to login page
        return render_template("register_success.html")

    else:
        return render_template("register.html")


@app.route("/createrecipe", methods=["GET", "POST"])
@login_required
def createrecipe():
    """Create Recipe"""
    if request.method == "POST":

        if not request.form.get("recipe_name"):
            return apology("must provide recipe name", 400)

        # Ensure recipe name is unique
        elif (len(db.execute("SELECT * FROM recipes WHERE name = ?",request.form.get("recipe_name"))) != 0):
            return apology("must provide unique recipe name", 400)

        # Ensure dnumber of servings was submitted
        elif not request.form.get("servings"):
            return apology("must provide num,ebr of servings", 400)

        # Add recipe to database
        recipe_name = request.form.get("recipe_name")
        servings = request.form.get("servings")
        recipe_time = request.form.get("time")
        method = request.form.get("method")
        image = request.form.get("img")
        url = create_url(15)
        while (len(db.execute("SELECT * FROM recipes WHERE url = ?",url))!= 0):
            url = create_url(15)

        db.execute("INSERT INTO recipes (user_id, name, servings, time, method, image, url) VALUES (?, ?, ?, ?, ?, ?, ?)", session["user_id"], recipe_name, servings, recipe_time, method, image, url)

        recipe_id = db.execute("SELECT id FROM recipes WHERE name = ?",recipe_name)
        for amount, units, ingredient in zip(request.form.getlist('amount'), request.form.getlist('units'), request.form.getlist('ingredient_name')):
            db.execute("INSERT INTO ingredients (name, recipe_id, amount, unit) VALUES (?, ?, ?, ?)", ingredient, recipe_id[0]["id"], amount, units)

        return redirect("/recipes")

    else:
        return render_template("createrecipe.html")

@app.route("/recipes", methods=["GET"])
@login_required
def recipes():
    user_recipes = db.execute("SELECT * FROM recipes WHERE user_id = ?", session["user_id"])
    total = 0
    recipes = []
    for row in user_recipes:
        recipe = {}
        recipe["name"] = row["name"]
        recipe["servings"] = int(row["servings"])
        recipe["time"] = row["time"]
        recipe["image"] = row["image"]
        recipe["url"] = row["url"]
        total = total + 1
        recipes.append(recipe)

    return render_template("recipes.html", total=total, recipes = recipes)

@app.route("/recipes/<recipe_url>", methods=["GET", "POST"])
@login_required
def recipe(recipe_url):

    if request.method == "POST":

        recipe = db.execute("SELECT * FROM recipes WHERE url = ?", recipe_url)
        db.execute("DELETE FROM ingredients WHERE recipe_id = ?", recipe[0]["id"])
        db.execute("DELETE FROM recipes_in_plans WHERE recipe_id = ?", recipe[0]["id"])
        db.execute("DELETE FROM recipes WHERE id = ?", recipe[0]["id"])
        return redirect("/recipes")

    else:

        user = db.execute("SELECT user_id FROM recipes WHERE url = ?", recipe_url)
        if (user[0]["user_id"] != session["user_id"]):
            return redirect("/recipes")

        else:
            recipe = db.execute("SELECT * FROM recipes WHERE url = ?", recipe_url)
            name = recipe[0]["name"]
            servings = recipe[0]["servings"]
            time = recipe[0]["time"]
            image = recipe[0]["image"]
            method = recipe[0]["method"]

            recipe_ing = db.execute("SELECT * FROM ingredients WHERE recipe_id = ?", recipe[0]["id"])
            ingredients = []
            for row in recipe_ing:
                ingredient = {}
                ingredient["name"] = row["name"]
                ingredient["amount"] = row["amount"]
                if (row["unit"] == "units"):
                    ingredient["units"] = ""
                else:
                    ingredient["units"] = row["unit"]
                ingredients.append(ingredient)

            return render_template("recipe.html", name=name, servings=servings, time=time, image=image, method=method, ingredients=ingredients, url=recipe_url)

@app.route("/recipes/<recipe_url>/edit", methods=["GET", "POST"])
@login_required
def editrecipe(recipe_url):

    if request.method == "POST":

        if not request.form.get("recipe_name"):
            return apology("must provide recipe name", 400)

        # Ensure dnumber of servings was submitted
        elif not request.form.get("servings"):
            return apology("must provide num,ebr of servings", 400)

        recipe = db.execute("SELECT * FROM recipes WHERE url = ?", recipe_url)
        db.execute("UPDATE recipes SET name = ?, servings = ?, time = ?, method = ?, image = ? WHERE id = ?",
                   request.form.get("recipe_name"), request.form.get("servings"), request.form.get("time"), request.form.get("method"), request.form.get("img"), recipe[0]["id"])

        db.execute("DELETE FROM ingredients WHERE recipe_id = ?", recipe[0]["id"])
        for amount, units, ingredient in zip(request.form.getlist('amount'), request.form.getlist('units'), request.form.getlist('ingredient_name')):
            db.execute("INSERT INTO ingredients (name, recipe_id, amount, unit) VALUES (?, ?, ?, ?)", ingredient, recipe[0]["id"], amount, units)
        return redirect("/recipes")

    else:
        user = db.execute("SELECT user_id FROM recipes WHERE url = ?", recipe_url)
        if (user[0]["user_id"] != session["user_id"]):
            return redirect("/recipes")

        else:
            recipe = db.execute("SELECT * FROM recipes WHERE url = ?", recipe_url)
            name = recipe[0]["name"]
            servings = recipe[0]["servings"]
            time = recipe[0]["time"]
            image = recipe[0]["image"]
            method = recipe[0]["method"]

            recipe_ing = db.execute("SELECT * FROM ingredients WHERE recipe_id = ?", recipe[0]["id"])
            ingredients = []
            for row in recipe_ing:
                ingredient = {}
                ingredient["name"] = row["name"]
                ingredient["amount"] = row["amount"]
                ingredient["units"] = row["unit"]
                ingredients.append(ingredient)

            return render_template("editrecipe.html", name=name, servings=servings, time=time, image=image, method=method, ingredients=ingredients, url=recipe_url)

@app.route("/createplan", methods=["GET", "POST"])
@login_required
def createplan():
    """Create Meal Plan"""
    if request.method == "POST":

        if not request.form.get("plan_name"):
            return apology("must provide recipe name", 400)

        # Ensure recipe name is unique
        elif (len(db.execute("SELECT * FROM plans WHERE name = ?",request.form.get("plan_name"))) != 0):
            return apology("must provide unique plan name", 400)

        # Ensure dnumber of servings was submitted
        elif not request.form.get("days"):
            return apology("must provide number of days", 400)

        # Add recipe to database
        plan_name = request.form.get("plan_name")
        plan_days = request.form.get("days")
        plan_people = request.form.get("people")
        url = create_url(15)
        while (len(db.execute("SELECT * FROM plans WHERE url = ?",url))!= 0):
            url = create_url(15)

        db.execute("INSERT INTO plans (user_id, name, days, people, url) VALUES (?, ?, ?, ?, ?)", session["user_id"], plan_name, plan_days, plan_people, url)

        plan_id = db.execute("SELECT id FROM plans WHERE name = ?",plan_name)
        for recipe_name, portions, adding in zip(request.form.getlist('recipe_name'), request.form.getlist('portions'), request.form.getlist('addThisRecipe')):
            if (adding == "- Remove"):
                if (int(portions) <= 0):
                    portions = '1'
                recipe_id = db.execute("SELECT id FROM recipes WHERE name = ?",recipe_name)
                db.execute("INSERT INTO recipes_in_plans (plan_id, recipe_id, portions) VALUES (?, ?, ?)", plan_id[0]["id"], recipe_id[0]["id"], int(portions))

        return redirect("/")

    else:
        user_recipes = db.execute("SELECT * FROM recipes WHERE user_id = ?", session["user_id"])
        recipes = []
        for row in user_recipes:
            recipe = {}
            recipe["name"] = row["name"]
            recipe["servings"] = int(row["servings"])
            recipe["time"] = row["time"]
            recipe["image"] = row["image"]
            recipe["url"] = row["url"]
            recipes.append(recipe)
        return render_template("createplan.html", recipes=recipes)

@app.route("/plans", methods=["GET"])
@login_required
def plans():
    user_plans = db.execute("SELECT * FROM plans WHERE user_id = ?", session["user_id"])
    total = 0
    plans = []
    for row in user_plans:
        plan = {}
        plan["name"] = row["name"]
        plan["days"] = int(row["days"])
        plan["people"] = row["people"]
        plan["url"] = row["url"]
        total = total + 1
        plans.append(plan)

    return render_template("plans.html", total=total, plans = plans)

@app.route("/plans/<plan_url>", methods=["GET", "POST"])
@login_required
def plan(plan_url):

    if request.method == "POST":

        plan = db.execute("SELECT * FROM plans WHERE url = ?", plan_url)
        db.execute("DELETE FROM recipes_in_plans WHERE plan_id = ?", plan[0]["id"])
        db.execute("DELETE FROM plans WHERE id = ?", plan[0]["id"])
        return redirect("/plans")

    else:

        user = db.execute("SELECT user_id FROM plans WHERE url = ?", plan_url)
        if (user[0]["user_id"] != session["user_id"]):
            return redirect("/plans")

        else:
            plan = db.execute("SELECT * FROM plans WHERE url = ?", plan_url)
            name = plan[0]["name"]
            days = plan[0]["days"]
            people = plan[0]["people"]

            recipes_in_plan = db.execute("SELECT * FROM recipes_in_plans WHERE plan_id = ?", plan[0]["id"])
            ingredients = []
            recipes = []
            for row in recipes_in_plan:
                recipe_ing = db.execute("SELECT * FROM ingredients WHERE recipe_id = ?", row["recipe_id"])
                for ing in recipe_ing:

                    if ing["unit"] == "cups":
                        ing["amount"] = float_to_string(float(ing["amount"]) * 16)
                        ing["unit"] = "tbsp"
                    elif ing["unit"] == "tsp":
                        ing["amount"] = float_to_string(float(ing["amount"])/3)
                        ing["unit"] = "tbsp"

                    in_list = is_ingredient_in_list(ingredients, ing["name"], ing["unit"])
                    if in_list == None:
                        ingredient = {}
                        ingredient["name"] = ing["name"]
                        ingredient["amount"] = float_to_string(float(ing["amount"]) * float(row["portions"]))
                        if (ing["unit"] == "units"):
                            ingredient["units"] = ""
                        else:
                            ingredient["units"] = ing["unit"]
                        ingredients.append(ingredient)
                    else:
                        ingredients [in_list]["amount"] = float_to_string(float(ingredients [in_list]["amount"]) + (float(ing["amount"]) * float(row["portions"])))

                recipe = {}
                this_recipe = db.execute("SELECT * FROM recipes WHERE id = ?", row["recipe_id"])
                recipe["name"] = this_recipe[0]["name"]
                recipe["portions"] = int(row["portions"])
                recipe["servings"] = this_recipe[0]["servings"]
                recipe["time"] = this_recipe[0]["time"]
                recipe["image"] = this_recipe[0]["image"]
                recipe["url"] = this_recipe[0]["url"]
                recipes.append(recipe)

            sorted_ingredients = sorted(ingredients, key=lambda ingredient: ingredient["name"])
            return render_template("plan.html", name=name, days=days, people=people, ingredients=sorted_ingredients, url=plan_url, recipes=recipes)

@app.route("/plans/<plan_url>/edit", methods=["GET", "POST"])
@login_required
def editplan(plan_url):

    if request.method == "POST":

        if not request.form.get("plan_name"):
            return apology("must provide recipe name", 400)

        # Ensure number of days was submitted
        elif not request.form.get("days"):
            return apology("must provide number of days", 400)

        # Change plan to database
        plan = db.execute("SELECT * FROM plans WHERE url = ?", plan_url)
        db.execute("UPDATE plans SET name = ?, days = ?, people = ? WHERE id = ?",
                   request.form.get("plan_name"), request.form.get("days"), request.form.get("people"), plan[0]["id"])

        db.execute("DELETE FROM recipes_in_plans WHERE plan_id = ?", plan[0]["id"])
        for recipe_name, portions, adding in zip(request.form.getlist('recipe_name'), request.form.getlist('portions'), request.form.getlist('addThisRecipe')):
            if (adding == "- Remove"):
                if (int(portions) <= 0):
                    portions = '1'
                recipe_id = db.execute("SELECT id FROM recipes WHERE name = ?",recipe_name)
                db.execute("INSERT INTO recipes_in_plans (plan_id, recipe_id, portions) VALUES (?, ?, ?)", plan[0]["id"], recipe_id[0]["id"], int(portions))

        return redirect("/plans")


    else:
        user = db.execute("SELECT user_id FROM plans WHERE url = ?", plan_url)
        if (user[0]["user_id"] != session["user_id"]):
            return redirect("/plans")

        else:
            plan = db.execute("SELECT * FROM plans WHERE url = ?", plan_url)
            name = plan[0]["name"]
            days = plan[0]["days"]
            people = plan[0]["people"]

            user_recipes = db.execute("SELECT * FROM recipes WHERE user_id = ?", session["user_id"])
            plan_recipes = db.execute("SELECT * FROM recipes_in_plans WHERE plan_id = ?", plan[0]["id"])
            recipes = []
            for row in user_recipes:
                recipe = {}
                recipe["name"] = row["name"]
                recipe["servings"] = int(row["servings"])
                recipe["time"] = row["time"]
                recipe["image"] = row["image"]
                recipe["url"] = row["url"]
                recipe["portions"] = 0
                recipe["button_class"] = "button-orange"
                recipe["added"] = "+ Add"

                for rcp in plan_recipes:
                    if row["id"] == rcp["recipe_id"]:
                        recipe["portions"] = rcp["portions"]
                        recipe["button_class"] = "button-green"
                        recipe["added"] = "- Remove"
                        break

                recipes.append(recipe)

            return render_template("editplan.html", name=name, days=days, people=people, recipes=recipes, url=plan_url)
