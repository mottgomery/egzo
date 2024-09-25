from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect
from base64 import b64encode
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zadachi.db'
app.config['UPLOAD_FOLDER'] = 'uploads/'  # Папка для хранения загруженных файлов
db = SQLAlchemy(app)


# Модель задачи
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    zad = db.Column(db.LargeBinary, nullable=False)  # Фото задачи
    resh = db.Column(db.LargeBinary, nullable=False)  # Фото решения
    level = db.Column(db.Integer, nullable=False)  # Уровень задачи


# Главная страница
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


# Страница со всеми задачами
@app.route('/posts')
def posts():
    sort_by = request.args.get('sort_by', 'level')  # Сортировка по умолчанию
    if sort_by == 'title':
        posts = Post.query.order_by(Post.title).all()
    else:
        posts = Post.query.order_by(Post.level).all()

    return render_template('posts.html', posts=posts)


# Добавление новой задачи
@app.route('/create', methods=["GET", "POST"])
def create():
    if request.method == "POST":
        title = request.form['title']
        level = request.form['level']

        # Загрузка файлов задачи и решения
        zad_file = request.files['zad']
        resh_file = request.files['resh']

        if zad_file and resh_file:
            zad_data = zad_file.read()  # Чтение бинарных данных файла задачи
            resh_data = resh_file.read()  # Чтение бинарных данных файла решения

            # Создание нового объекта Post
            new_post = Post(title=title, zad=zad_data, resh=resh_data, level=int(level))

            try:
                db.session.add(new_post)
                db.session.commit()
                return redirect('/posts')
            except:
                return 'Произошла ошибка при добавлении задачи'
        else:
            return 'Ошибка: Необходимо загрузить оба файла - задачу и решение.'

    return render_template('create.html')


# Страница "О проекте"
@app.route('/about')
def about():
    return render_template('about.html')


# Функция для отображения изображений в формате Base64
def to_base64(binary_data):
    return b64encode(binary_data).decode('utf-8')


# Добавление функции в шаблон
app.jinja_env.filters['to_base64'] = to_base64

if __name__ == '__main__':
    # Создание папки для загрузки файлов, если она не существует
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    app.run(debug=True)
