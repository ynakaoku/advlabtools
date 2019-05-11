from flask import Blueprint, flash, g, redirect, render_template, request, url_for, Flask
#from werkzeug.exceptions import abort
#from flaskr.auth import login_required
#from flaskr.db import get_db
import os
import dash
import dash_renderer
import dash_core_components as dcc
import dash_html_components as html

server = Flask(__name__)
dash_app = dash.Dash(__name__, server=server, url_base_pathname='/dummy/') 

dash_app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),
    html.Div(children='''
        Dash: A web application framework for Python.
    '''),
    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montreal'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    )
])

bp = Blueprint('dashboards', __name__, url_prefix='/dashboards')

@bp.route('/select', methods=['GET', 'POST'])
def index():
    return render_template('dashboards/select.html')

@bp.route('/dash_one', methods=['GET', 'POST'])
def dash_one():
	return dash_app.index()

server.run(host='0.0.0.0', port=8080)
