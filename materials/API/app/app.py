from flask import Flask, request, jsonify
import psycopg2
import psycopg2.extras
import json
import pandas as pd


database_uri = "postgresql://postgres:postgres@0.0.0.0:5432/postgres"

app = Flask(__name__)
conn = psycopg2.connect(database_uri)


@app.route("/")
def home():
    cur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    cur.execute('select * from flights limit 10;')
    results = cur.fetchall()
    cur.close()
    return json.dumps([x._asdict() for x in results], default=str)


@app.route("/month")
def monthly():
    month = request.args.get('month')
    cur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    cur.execute(f'select * from flights where month = {month} ')
    results = cur.fetchall()
    cur.close()
    return json.dumps([x._asdict() for x in results], default=str)


@app.route("/monthDay")
def monthday():
    month = request.args.get('month')
    day = request.args.get('day')
    results = pd.read_sql(f'select * from flights where month = {month} and day={day}', conn)
    return results.to_json(orient='records')


@app.route('/user', methods=['POST', 'GET', 'DELETE', 'PATCH'])
def user():
    if request.method == 'GET':
        cur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        user_id = request.args.get('id')
        cur.execute(f'select * from users where id={user_id}')
        results = cur.fetchone()
        cur.close()
        return json.dumps(results._asdict(), default=str)
    if request.method == 'POST':
        user = request.json
        cur = conn.cursor()
        cur.execute('insert into users (name, lastname, age) values (%s, %s, %s)',
                    (user['name'], user['lastname'], user['age']))
        conn.commit()
        cur.execute('SELECT LASTVAL()')
        user_id = cur.fetchone()[0]
        cur.close()
        return json.dumps({'user_id': user_id})
    if request.method == 'DELETE':
        cur = conn.cursor()
        user_id = request.args.get('id')
        cur.execute(f'delete from users where id={user_id}')
        conn.commit()
        cur.close()
        return json.dumps({'user_id': user_id})
    if request.method == 'PATCH':
        user = request.json
        cur = conn.cursor()
        user_id = request.args.get('id')
        cur.execute('update users set (name, lastname, age) = (%s,%s,%s) where id=%s ',
                    (user['name'], user['lastname'], user['age'], user_id))
        conn.commit()
        cur.close()
        return json.dumps({'user_id': user_id})


@app.route('/users', methods=['POST', 'GET', 'DELETE', 'PATCH'])
def users():
    if request.method == 'GET':
        cur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        cur.execute(f'select * from users')
        results = cur.fetchone()
        cur.close()
        return json.dumps([x._asdict() for x in results], default=str)
    if request.method == 'POST':
        cur = conn.cursor()
        users = request.json
        users_list = [(user['name'], user['lastname'], user['age']) for user in users]
        cur.executemany('insert into users (name, lastname, age) values (%s, %s, %s)', users_list)
        conn.commit()
        cur.close()
        return  "Correct!!"



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
