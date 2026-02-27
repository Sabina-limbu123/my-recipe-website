from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    recipes = db.relationship('Recipe', backref='author', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    recipes = db.relationship('Recipe', backref='category', lazy=True)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    recipes = Recipe.query.all()
    return render_template('index.html', recipes=recipes)

@app.route('/recipe/<int:id>')
def recipe_detail(id):
    recipe = Recipe.query.get_or_404(id)
    return render_template('recipe_detail.html', recipe=recipe)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        flash("Invalid credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        hashed = generate_password_hash(request.form['password'])
        user = User(
            username=request.form['username'],
            email=request.form['email'],
            password=hashed
        )
        db.session.add(user)
        db.session.commit()
        flash("Registration successful!")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    results = []

    if query:
        results = Recipe.query.filter(Recipe.title.contains(query)).all()

    return render_template('search.html', results=results)
@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        if not Category.query.first():
            breakfast = Category(name="Breakfast")
            lunch = Category(name="Lunch")
            dinner = Category(name="Dinner")
            
            db.session.add_all([breakfast, lunch, dinner, ])
            db.session.commit()

        if not User.query.filter_by(email="admin@gmail.com").first():
            admin = User(
                username="admin",
                email="admin@gmail.com",
                password=generate_password_hash("admin123")
            )
            db.session.add(admin)
            db.session.commit()
            
        if not Recipe.query.first():

            admin = User.query.filter_by(email="admin@gmail.com").first()
            breakfast = Category.query.filter_by(name="Breakfast").first()
            lunch = Category.query.filter_by(name="Lunch").first()
            dinner = Category.query.filter_by(name="Dinner").first()
           

            recipes = [

                Recipe(
                    title="Creamy Garlic Chicken",
                    description="Juicy chicken cooked in creamy garlic sauce.",
                    ingredients="Chicken breast, Garlic, Cream, Butter, Salt, Pepper.",
                    instructions="1. Heat butter.\n2. Add garlic.\n3. Cook chicken.\n4. Add cream and simmer until thick.",
                    image="cgc.jpg",
                    user_id=admin.id,
                    category_id=dinner.id
                ),

                Recipe(
                    title="Classic Pancakes",
                    description="Fluffy and soft breakfast pancakes.",
                    ingredients="Flour, Eggs, Milk, Sugar, Baking powder.",
                    instructions="1. Mix dry ingredients.\n2. Add milk and eggs.\n3. Cook on pan until golden.",
                    image="pancake.jpg",
                    user_id=admin.id,
                    category_id=breakfast.id
                ),

                Recipe(
                    title="Spaghetti Bolognese",
                    description="Italian pasta with rich meat sauce.",
                    ingredients="Spaghetti, Minced beef, Tomato sauce, Onion, Garlic.",
                    instructions="1. Cook beef.\n2. Add tomato sauce.\n3. Boil pasta.\n4. Combine and serve.",
                    image="ss.jpg",
                    user_id=admin.id,
                    category_id=dinner.id
                ),

                Recipe(
                    title="Vegetable Stir Fry",
                    description="Healthy mixed vegetable dish full of flavor.",
                    ingredients="Broccoli, Carrot, Bell pepper, Soy sauce.",
                    instructions="1. Stir fry vegetables.\n2. Add soy sauce.\n3. Cook 5 minutes and serve.",
                    image="jj.jpg",
                    user_id=admin.id,
                    category_id=lunch.id
                ),

                Recipe(
                    title="Chocolate Brownies",
                    description="Rich and fudgy chocolate brownies.",
                    ingredients="Cocoa powder, Flour, Eggs, Sugar, Butter.",
                    instructions="1. Mix ingredients.\n2. Bake at 180°C for 25 minutes.\n3. Let cool and serve.",
                    image="cc.jpg",
                    user_id=admin.id,
                    category_id=breakfast.id
                ),
                Recipe(
                title="Chicken Momo",
                description="Steamed dumplings filled with juicy spiced chicken.",
                ingredients="Minced chicken, Onion, Garlic, Ginger, Cabbage, Flour, Salt, Pepper, Soy sauce.",
                instructions="1. Mix chicken with chopped onion, cabbage, ginger, garlic and spices.\n2. Prepare dough using flour and water.\n3. Roll small circles and add filling inside.\n4. Fold and seal the dumplings.\n5. Steam for 10-12 minutes until cooked.",
                image="momo.jpg",
                user_id=admin.id,
                category_id=breakfast.id
            )
            ]

            db.session.add_all(recipes)
            db.session.commit()

   
    if __name__ == "__main__":
        app.run()