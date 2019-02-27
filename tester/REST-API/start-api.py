# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, Markup, abort, make_response
# import peewee
# import json

api = Flask(__name__)

@api.route('/')
def index():
    html = '''
    <form action="/iperf3test">
        <p><label>iperf3 test: </label></p>
        Test Name: <input type="text" name="TestName"></p>
        Config File: <input type="text" name="ConfigFile"></p>
        Interval: <input type="text" name="Interval" value="1"></p>
        Bandwidth: <input type="text" name="Bandwidth" value="1G"></p>
        MSS: <input type="text" name="MSS" value="1460"></p>
        Parallel: <input type="text" name="Parallel" value="1"></p>
        Time: <input type="text" name="Time" value="10"></p>
        Protocol is UDP? : <input type="checkbox" name="UDP?"></p>
        Use Server Output? : <input type="checkbox" name="Get Server Output?"></p>
        Use ESXTOP Output? : <input type="checkbox" name="Get ESXTOP Output?"></p>
        <button type="submit" formmethod="get">GET</button></p>
        <button type="submit" formmethod="post">POST</button></p>
    </form>
    '''
    return Markup(html)

@api.route('/iperf3test', methods=['GET', 'POST'])
def iperf3test():
    try:
        if request.method == 'POST':
            return request.form['TestName']
        else:
            return request.args.get('TestName', '')
    except Exception as e:
        return str(e)

@api.route('/sayHello', methods=['GET'])
def say_hello():

    result = {
        "result":True,
        "data": "Hello, world!"
        }

    return make_response(jsonify(result))
    # if you do not want to use Unicode: 
    # return make_response(json.dumps(result, ensure_ascii=False))

@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    api.run(host='0.0.0.0', port=8000)
