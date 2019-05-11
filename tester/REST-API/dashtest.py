from dash import Dash
#from werkzeug.wsgi import DispatcherMiddleware
import flask
#from werkzeug.serving import run_simple
import dash_html_components as html

server = flask.Flask(__name__)
dash_app1 = Dash(__name__, server = server, url_base_pathname='/dashboard/' )
dash_app2 = Dash(__name__, server = server, url_base_pathname='/reports/')
dash_app1.layout = html.Div([html.H1('Hi there, I am app1 for dashboards')])
dash_app2.layout = html.Div([html.H1('Hi there, I am app2 for reports')])
@server.route('/')
@server.route('/hello')
def hello():
    return 'hello world!'

@server.route('/dashboard')
def render_dashboard():
    return flask.redirect('/dash1')


@server.route('/reports')
def render_reports():
    return flask.redirect('/dash2')

#app = DispatcherMiddleware(server, {
#    '/dash1': dash_app1.server,
#    '/dash2': dash_app2.server
#})

server.run(host='0.0.0.0', port=8080)
