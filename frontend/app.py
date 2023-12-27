from flask import Flask, url_for, render_template, redirect
from markupsafe import escape

app = Flask(__name__)


@app.route('/')
def redir():
    return redirect('/hello/')


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('test.html', name=name)

