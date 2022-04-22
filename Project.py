from flask import redirect, render_template, flash, Blueprint, request, url_for
from flask_login import login_required, current_user, login_user, UserMixin
from flask import current_app as app
from .forms import LoginForm, SignupForm
from .models import db, User
from . import login_manager
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from telebot import types
import telebot;

auth_bp = Blueprint('auth_bp', __name__,
                    template_folder='templates',
                    static_folder='static')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    signup_form = SignupForm()
    if request.method == 'POST':
        if signup_form.validate_on_submit():
            name = signup_form.data['name']
            email = signup_form.data['email']
            password = signup_form.data['password']
            existing_user = User.query.filter_by(email=email).first()
            if existing_user is None:
                user = User(name=name,
                            email=email)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect('/home')
            error = dict(head='Ошибка регистрации', body='Такой пользователь уже существует')
            return render_template('error.html', error=error)
    return render_template('signup.html',
                           title='Create an Account.',
                           form=SignupForm(),
                           template='signup-page',
                           body="Sign up for a user account.")


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if request.method == 'POST':
        if login_form.validate_on_submit():
            name = login_form.data['name']
            email = login_form.data['email']
            password = login_form.data['password']
            user = User.query.filter_by(email=email).first()
            if user:
                if user.check_password(password):
                    login_user(user)
                    return redirect('/home')
            error = dict(head='Ошибка авторизации', body='Такого пользователя не существует')
            return render_template('error.html', error=error)
    return render_template('login.html',
                           title='Create an Account.',
                           form=LoginForm(),
                           template='signup-page',
                           body="Sign up for a user account.")


@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth_bp.login'))


class LoginForm(FlaskForm):
    name = StringField('Имя',
                       validators=[DataRequired()])
    email = StringField('Электронный адресс',
                        validators=[Length(min=6),
                                    Email(message='Введите правильный электронный адресс.'),
                                    DataRequired()])
    password = PasswordField('Пароль',
                             validators=[DataRequired(),
                                         Length(min=6, message='Select a stronger password.')])
    confirm = PasswordField('Подтвердите пароль',
                            validators=[DataRequired(),
                                        EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Вход')


class SignupForm(FlaskForm):
    name = StringField('Имя',
                       validators=[DataRequired()])
    email = StringField('Электронный адрес',
                        validators=[Length(min=6),
                                    Email(message='Enter a valid email.'),
                                    DataRequired()])
    password = PasswordField('Пароль',
                             validators=[DataRequired(),
                                         Length(min=6, message='Пароль недостаточно надежный.')])
    confirm = PasswordField('Подтвердите пароль',
                            validators=[DataRequired(),
                                        EqualTo('password', message='Пароли должны совпадать.')])
    submit = SubmitField('Регистрация')


class UploadForm(FlaskForm):
    lat = StringField('lat', validators=[DataRequired()])
    lng = StringField('lng', validators=[DataRequired()])
    name = StringField('Название', validators=[DataRequired()])
    desc = StringField('Описание', validators=[DataRequired()])
    photo = FileField(validators=[FileRequired()])
    submit = SubmitField('Регистрация')


class User(UserMixin, db.Model):
    __tablename__ = 'flasklogin-users'

    id = db.Column(db.Integer,
                   primary_key=True)
    name = db.Column(db.String,
                     nullable=False,
                     unique=False)
    email = db.Column(db.String(40),
                      unique=True,
                      nullable=False)
    password = db.Column(db.String(200),
                         primary_key=False,
                         unique=False,
                         nullable=False)
    created_on = db.Column(db.DateTime,
                           index=False,
                           unique=False,
                           nullable=True)
    last_login = db.Column(db.DateTime,
                           index=False,
                           unique=False,
                           nullable=True)

    def set_password(self, password):
        self.password = generate_password_hash(bytes(password, encoding='utf-8'), method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password, password)


bot = telebot.TeleBot('5318366610:AAF5Z6-zcRI7AULLOBckBDbp7PVwjxkqJtA');

name = '';
surname = '';
age = 0;


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/reg':
        bot.send_message(message.from_user.id, "Как тебя зовут?");
        bot.register_next_step_handler(message, get_name);
    else:
        bot.send_message(message.from_user.id, 'Напиши /reg');


def get_name(message):
    global name;
    name = message.text;
    bot.send_message(message.from_user.id, 'Какая у тебя фамилия?');
    bot.register_next_step_handler(message, get_surnme);


def get_surname(message):
    global surname;
    surname = message.text;
    bot.send_message('Сколько тебе лет?');
    bot.register_next_step_handler(message, get_age);


def get_age(message):
    global age;
    while age == 0:
        try:
            age = int(message.text)
        except Exception:
            bot.send_message(message.from_user.id, 'Цифрами, пожалуйста');
    keyboard = types.InlineKeyboardMarkup();
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes');
    keyboard.add(key_yes);
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no');
    keyboard.add(key_no);
    question = 'Тебе ' + str(age) + ' лет, тебя зовут ' + name + ' ' + surname + '?';
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":
        bot.send_message(call.message.chat.id, 'Запомню : )');
    elif call.data == "no":

        TIMEOUT_CONNECTION = 5

        START_MESSAGE = """Отправь мне выражение, а я тебе скажу ответ)"""

        HELP_MESSAGE = """Вы мне отправляете выражение, а я вам возвращаю его результат.
        ***Операторы***:
            + - сложение;
            - - вычитание;
            \* - умножение;
            / - деление;
            \*\* - возведение в степнь.

        ***Функции***:
            cos(x) - косинус x;
            sin(x) - синус x;
            tg(x) - тангенс x;
            fact(x) - факториал x;
            sqrt(x) - квадратный корень х;
            sqr(x) - х в квадрате.
        ***Логарифмы***:
            log2(x) - логарифм х по основанию 2;
            lg(х) - десятичный логарифм х;
            ln(x) - натуральный логарифм x;
            log(b, х) - логарифм х по основанию b;
        ***Системы счисления***:
            0bx - перевести двоичное число х в десятичное;
            0ox - перевести восьмиричное число х в десятичное;
            0xx - перевести шестнадцатиричное число х в десятичное;"""

        пи = п = p = pi = 3.141592653589793238462643

        def fact(float_):
            return math.factorial(float_)

        def cos(float_):
            return math.cos(float_)

        def sin(float_):
            return math.sin(float_)

        def tg(float_):
            return math.tan(float_)

        def tan(float_):
            return math.tan(float_)

        def ln(float_):
            return math.log(float_)

        def log(base, float_):
            return math.log(float_, base)

        def lg(float_):
            return math.log10(float_)

        def log2(float_):
            return math.log2(float_)

        def exp(float_):
            return math.exp(float_)

        @bot.message_handler(commands=['start', 'help'])
        def send_start(message):
            print('%s (%s): %s' % (message.chat.first_name, message.chat.username, message.text))
            msg = None

            if message.text.lower() == '/start':
                msg = bot.send_message(message.chat.id, START_MESSAGE, parse_mode='markdown')

            elif message.text.lower() == '/help':
                msg = bot.send_message(message.chat.id, HELP_MESSAGE, parse_mode='markdown')

            if (msg):
                print('Бот: %s' % msg.text)

        @bot.message_handler(func=lambda message: True)
        def answer_to_user(message):
            print('%s (%s): %s' % (message.chat.first_name, message.chat.username, message.text))
            msg = None

            user_message = message.text.lower()

            if BOT_NAME:
                regex = re.compile(BOT_NAME.lower())
                print(regex.search(user_message))
                if regex.search(user_message) == None:
                    return

                regex = re.compile('%s[^a-z]' % (BOT_NAME.lower()))
                user_message = regex.sub("", user_message)

            user_message = user_message.lstrip()
            user_message = user_message.rstrip()

            print(user_message)

            if user_message == 'привет':
                msg = bot.send_message(message.chat.id, '*Привет, %s*' % (message.chat.first_name),
                                       parse_mode='markdown')

            elif user_message == 'помощь':
                msg = bot.send_message(message.chat.id, HELP_MESSAGE, parse_mode='markdown')

            else:
                try:
                    answer = str(eval(user_message.replace(' ', '')))
                    msg = bot.send_message(message.chat.id, user_message.replace(' ', '') + ' = ' + answer)

                except SyntaxError:
                    msg = bot.send_message(message.chat.id,
                                           'Похоже, что вы написали что-то не так. \nИсравьте ошибку и повторите снова')
                except NameError:
                    msg = bot.send_message(message.chat.id,
                                           'Переменную которую вы спрашиваете я не знаю. \nИсравьте ошибку и повторите снова')
                except TypeError:
                    msg = bot.send_message(message.chat.id,
                                           'Мне кажется, что в выражении присутствует ошибка типов. \nИсравьте ошибку и повторите снова')
                except ZeroDivisionError:
                    msg = bot.send_message(message.chat.id,
                                           'В выражении вы делите на ноль. \nИсравьте ошибку и повторите снова')

            if (msg):
                print('Бот: %s' % msg.text)

        @bot.inline_handler(func=lambda query: True)
        def inline_answer_to_user(inline_query):
            answer = 0
            answer_list = []
            try:
                answer = str(eval(inline_query.query.lower().replace(' ', '')))
                answer_to_send = answer.replace('*', '\*')
                query_to_send = inline_query.query.replace('*', '\*').lower().replace(' ', '')

                answer_list.append(types.InlineQueryResultArticle(
                    id=0,
                    title='Отправить с выражением',
                    description='%s = %s' % (inline_query.query, answer),
                    input_message_content=types.InputTextMessageContent(
                        message_text='%s = *%s*' % (query_to_send, answer_to_send),
                        parse_mode='markdown'),
                    thumb_url=WITH_ICON
                ))

                answer_list.append(types.InlineQueryResultArticle(
                    id=1,
                    title='Отправить без выражения',
                    description='%s' % (answer),
                    input_message_content=types.InputTextMessageContent(
                        message_text='*%s*' % (answer_to_send),
                        parse_mode='markdown'),
                    thumb_url=WITHOUT_ICON
                ))

            except SyntaxError:
                answer = False
            except NameError:
                answer = False
            except TypeError:
                answer = False
            except ZeroDivisionError:
                answer = False

            if (not answer):
                answer_list = []
                answer_list.append(types.InlineQueryResultArticle(
                    id=0,
                    title='Калькулятор',
                    description='Чтобы посичтать выражение - введите его.\nЕсли вы хотите просмотреть справку, то перейдите в диалог со мной и напишите \"/help\"',
                    input_message_content=types.InputTextMessageContent(
                        message_text='Я хотел посчитать выражение, но нажал не туда')
                ))

            bot.answer_inline_query(inline_query.id, answer_list)

        if (__name__ == '__main__'):
            while True:
                try:
                    bot.polling(none_stop=True)
                except Exception as e:
                    print('Ошибка подключения. Попытка подключения через %s сек.' % TIMEOUT_CONNECTION)
                    time.sleep(TIMEOUT_CONNECTION)


@bot.message_handler(commands=['help', 'помощь'])
def ask_(message):
    bot.send_message(message.chat.id, "Список команд бота: \n" +
                     "/start - начало работы бота \n" +
                     "/clas - вывести классификацию важных ударений \n" +
                     "/mistakes - вывести cписок ваших ошибок \n" +
                     "/stat - вывести статистику (число верных ответов, процент верных) \n" +
                     "/deletestat4 - удалить статистику ответов и ошибок в 4 задании \n" +
                     "/deletestat7 - удалить статистику ответов и ошибок в 7 задании \n" +
                     "/number4 - выбрать 4 задание ЕГЭ задание для выполнения (нажать только после /start) \n" +
                     "/number7 - выбрать 7 задание ЕГЭ задание для выполнения (нажать только после /start) \n" +
                     "/help - вывести cписок команд бота \n")


@bot.message_handler(commands=['clas', 'классификация'])
def clas(message):
    bot.send_message(message.chat.id, '\n'.join(c))


@bot.message_handler(commands=['stat', 'statistics', 'статистика'])
def stat(message):
    if (not message.chat.id in d):
        bot.send_message(message.chat.id,
                         "Вы еще не отвечали, используйте /start для начала работы или посмотрите список всех команд в /help")
        return

    if (mis4[message.chat.id][2]):
        p = mis4[message.chat.id][1]
        o = mis4[message.chat.id][2]
        bot.send_message(message.chat.id,
                         "Количество верных ответов в 4 задании: " + str(p) +
                         "\nКоличество всех ответов: " + str(o) +
                         "\nПроцент верных: " + str(100 * p / o) + " %\n")
    else:
        bot.send_message(message.chat.id, "Вы еще не отвечали на задание с ударениями\n")

    if (mis7[message.chat.id][2]):
        p = mis7[message.chat.id][1]  # количество верных ответов
        o = mis7[message.chat.id][2]  # количество всех ответов
        bot.send_message(message.chat.id,
                         "Количество верных ответов в 7 задании : " + str(p) +
                         "\nКоличество всех ответов: " + str(o) +
                         "\nПроцент верных: " + str(100 * p / o) + " %\n")
    else:
        bot.send_message(message.chat.id, "Вы еще не отвечали на задание с лексическими нормами\n")


@bot.message_handler(commands=['mistakes', 'mist', 'ошибки'])
def mistake(message):
    if (not message.chat.id in d):
        bot.send_message(message.chat.id,
                         "Вы еще не отвечали, используйте /start для начала работы или посмотрите список всех команд в /help")
        return

    if (len(mis4[message.chat.id][0])):
        bot.send_message(message.chat.id,
                         "В этих ударениях вы допускали ошибки:\n" + '\n'.join(mis4[message.chat.id][0]))
    if (len(mis7[message.chat.id][0])):
        bot.send_message(message.chat.id,
                         "В этих словах вы допускали ошибки:\n" + '\n'.join(mis7[message.chat.id][0]))
    if (len(mis4[message.chat.id][0]) + len(mis7[message.chat.id][0]) == 0):
        bot.send_message(message.chat.id, "Вы еще не ошибались")


@bot.message_handler(commands=['deletestat4'])
def deletestat_4(message):
    if (message.chat.id in d and mis4[message.chat.id][2]):
        bot.send_message(message.chat.id,
                         "Вы действительно хотите удалить свою статистику? Напишите ДА, чтобы подтвердить выбор.")
        d[message.chat.id][3] = 4
    else:
        bot.send_message(message.chat.id,
                         "Вы еще не отвечали, используйте  /start для начала работы или посмотрите список всех команд в  /help")


@bot.message_handler(commands=['deletestat7'])
def deletestat_7(message):
    if (message.chat.id in d and mis7[message.chat.id][2]):
        bot.send_message(message.chat.id,
                         "Вы действительно хотите удалить свою статистику? Напишите ДА, чтобы подтвердить выбор.")
        d[message.chat.id][3] = 7
    else:
        bot.send_message(message.chat.id,
                         "Вы еще не отвечали, используйте  /start для начала работы или посмотрите список всех команд в  /help")


@bot.message_handler(commands=['start', 'старт'])
def start(message):
    if (not message.chat.id in d):
        d[message.chat.id] = [0, 0, 0, 0]
        mis4[message.chat.id] = [[], 0, 0]
        mis7[message.chat.id] = [[], 0, 0]
    bot.send_message(message.chat.id, "Для повторения 4 задания (ударения) нажмите /number4. \n" +
                     "Для повторения 7 задания (лексические нормы: веера-вееры) нажмите /number7.",
                     reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['number4', 'номер4', '4', 'ударения', 'ударение', 'четыре'])
def number4(message):
    if (not message.chat.id in d):
        bot.send_message(message.chat.id,
                         "Для начала работы напишите /start или /help, чтобы посмотреть на все команды бота")
        return
    d[message.chat.id][2] = 4
    keyboard = buttons_4(message.chat.id)
    bot.send_message(message.chat.id, " Выберите из 2 варинтов", reply_markup=keyboard)


@bot.message_handler(commands=['number7', 'номер7', '7', '7номер', 'семь'])
def number7(message):
    if (not message.chat.id in d):
        bot.send_message(message.chat.id,
                         "Для начала работы напишите /start или /help, чтобы посмотреть на все команды бота")
        return
    d[message.chat.id][2] = 7
    keyboard = buttons_7(message.chat.id)
    bot.send_message(message.chat.id, "Выберите из 2 варинтов", reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def ask(message):
    if (not message.chat.id in d):
        bot.send_message(message.chat.id,
                         "Для начала работы напишите /start или /help, чтобы посмотреть на все команды бота")
        return

    if (message.text == "ДА"):
        if (d[message.chat.id][3] == 4):
            mis4[message.chat.id][0].clear()
            mis4[message.chat.id][1] = 0
            mis4[message.chat.id][2] = 0
        else:
            mis7[message.chat.id][0].clear()
            mis7[message.chat.id][1] = 0
            mis7[message.chat.id][2] = 0
        bot.send_message(message.chat.id, "Ваша статистика удалена")
        return
    d[message.chat.id][3] = 0

    s = message.text
    x = d[message.chat.id][0]

    if (d[message.chat.id][2] == 4):
        if (s == a[x][0]):
            keyboard = buttons_4(message.chat.id)
            bot.send_message(message.chat.id, a[x][0] + " -  ВЕРНО!", reply_markup=keyboard)
            mis4[message.chat.id][1] += 1
            mis4[message.chat.id][2] += 1
        elif (s == a[x][1]):
            mistakes_4(x, message.chat.id)
            keyboard = buttons_4(message.chat.id)
            bot.send_message(message.chat.id, a[x][1] + " - НЕВЕРНО!", reply_markup=keyboard)
            mis4[message.chat.id][2] += 1
    else:
        if (s == b[x][0]):
            keyboard = buttons_7(message.chat.id)
            bot.send_message(message.chat.id, b[x][0] + " -  ВЕРНО!", reply_markup=keyboard)
            mis7[message.chat.id][1] += 1
            mis7[message.chat.id][2] += 1
        elif (s == b[x][1]):
            keyboard = buttons_7(message.chat.id)
            mistakes_7(x, message.chat.id)
            bot.send_message(message.chat.id, b[x][1] + " - НЕВЕРНО!", reply_markup=keyboard)
            mis7[message.chat.id][2] += 1


def mistakes_4(x, id):
    if (not a[x][0] in mis4[id][0]):
        mis4[id][0].append(a[x][0])


def mistakes_7(x, id):
    if (not b[x][0] in mis7[id][0]):
        mis7[id][0].append(b[x][0])


def buttons_4(id):
    d[id][1] = d[id][0]
    m = randint(0, 1)
    k = randint(0, raz4 - 1)
    r = d[id][1]
    if (r == k):
        k = (k + 1) % raz4
    d[id][0] = k
    keyboard = types.ReplyKeyboardMarkup(True)
    key_1 = types.KeyboardButton(text=a[k][m])
    key_2 = types.KeyboardButton(text=a[k][(m + 1) % 2])
    keyboard.add(key_1, key_2)
    return keyboard


def buttons_7(id):
    d[id][1] = d[id][0]
    m = randint(0, 1)
    k = randint(0, raz7 - 1)
    r = d[id][1]
    if (r == k):
        k = (k + 1) % raz7
    d[id][0] = k
    keyboard = types.ReplyKeyboardMarkup(True)
    key_1 = types.KeyboardButton(text=b[k][m])
    key_2 = types.KeyboardButton(text=b[k][(m + 1) % 2])
    keyboard.add(key_1, key_2)
    return keyboard
bot.polling()
