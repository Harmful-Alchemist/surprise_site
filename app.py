from flask import Flask, render_template, url_for, request, redirect
from PIL import Image
import os
from math import sqrt
from config import dev_config
from werkzeug.utils import secure_filename
import flask_login

app = Flask(__name__)

config=dev_config
app.secret_key = config['secret_key']
p='Druk op de plattegrond waar je bent en babymans geeft aan of je in de buurt bent of niet. Ben je er dan zegt hij \'Hallo!\'.'

@app.route('/')
@flask_login.login_required
def home():
    current_img = config['current_img']
    return render_template('home.html', img_url=url_for('static', filename=current_img), location_url='/location', header = 'Vind het cadeau!', p = p)

@app.route('/location')
@flask_login.login_required
def location():
    current_img = config['current_img']
    im=Image.open(os.path.join('static',current_img))
    width, heigth = im.size
    max_distance = sqrt(width**2+heigth**2)

    hidden_x =  config['hidden_x']
    hidden_y =  config['hidden_y']
    location=list(request.args.keys())[0]
    x = int(location.split(',')[0])
    y = int(location.split(',')[1])

    distance = abs(sqrt( (x-hidden_x)**2 + (y-hidden_y)**2))

    current_audio = 'zeker_niet.wav'
    if distance>max_distance/2:
        current_audio = 'zeker_niet.wav'
    elif distance < 20:
        current_audio = 'gevonden.wav'
    elif distance<max_distance/5:
        current_audio = 'licht_enthousiats_ja.wav'
    elif distance<max_distance/4:
        current_audio = 'normale_ja.wav'
    elif distance<=max_distance/2:
        current_audio = 'normale_nee.wav'
    elif distance<11:
        current_audio = 'gevonden.wav'

    audio = url_for('static', filename=current_audio)

    return render_template('home.html', img_url=url_for('static', filename=current_img), location_url='/location', audio = audio, header = 'Vind het cadeau!', p=p)

@app.route('/hide')
@flask_login.login_required
def hide():
    current_img = config['current_img']
    if len(list(request.args.keys()))>0:
        location=list(request.args.keys())[0]
        x = int(location.split(',')[0])
        y = int(location.split(',')[1])
        config['hidden_x'] = x
        config['hidden_y'] = y
        return render_template('home.html', img_url=url_for('static', filename=current_img), location_url='/hide', header = 'Nieuwe verstopplaats gekozen x={} y={}!'.format(x, y), a='Terug naar zoeken!', href=url_for('home'))
    else:
        return render_template('home.html', img_url=url_for('static', filename=current_img), location_url='/hide', header = 'Klik op een nieuwe verstopplaats', a='Terug naar zoeken!', href=url_for('home'))

@app.route('/plans', methods=['GET', 'POST'])
@flask_login.login_required
def plans():
    images = filter(lambda fname: fname.endswith('.png') or fname.endswith('.gif') or fname.endswith('.jpeg')  ,os.listdir('static'))
    if request.method == 'GET':
        return render_template('plans.html', images = images, current_img = config['current_img'])
    elif request.method == 'POST':
        if len(request.files) == 1:
            f = request.files['file']
            f.save(os.path.join('static',secure_filename(f.filename)))
        elif request.form['action'] == 'Delete':
            if request.form['image_name'] == config['current_img']:
                return render_template('plans.html', images = images, current_img = config['current_img'], h2='Kan niet de geselecteerde plattegrond verwijderen!')
            try:
                os.remove(os.path.join('static' , request.form['image_name']))
            except OSError:
                app.logger.info('Could not delete file={}'.format(request.form['image_name']))
        elif request.form['action'] == 'Select':
            config['current_img'] = request.form['image_name']
            return redirect(url_for('hide'))

        return redirect(url_for('plans'))

# security stuff
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
class User(flask_login.UserMixin):
    def __init__(self, username):
        self.username=username
        self.id = username

    def __repr__():
        return 'User({})'.format(self.username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['user']
    password = request.form['pw']

    if config['username'] == username and config['password'] == password:
        user = User(username)
        flask_login.login_user(user)
        #should be some redirect checcking here
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))

# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')

@login_manager.user_loader
def load_user(userid):
    return User(userid)

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host="0.0.0.0")
