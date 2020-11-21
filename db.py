import sqlite3
from flask import g
from flask import Flask

DATABASE = 'data.db'
app=Flask(__name__)
def get_db():
    print("get_db called")
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    print("connection closed")
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def register_user(email,password):
    try:
        cur=get_db().execute("insert into users(email,password) values(?,?)",(email,password))
        get_db().commit()
        return "registration success"
    except sqlite3.IntegrityError as e:
        return "Email already exists"

def login_user(email,password):
        cur=get_db().execute("select * from users where email=? and password=?",(email,password))
        results=cur.fetchone()
        try:
            if results[1]==email and results[2]==password:
                return True
        except Exception as e:
            print(str(e))
        return False

def get_plan_type(email):
        try:
            cur=get_db().execute("select plan_type from users where email=?",(email,))
            results=cur.fetchone()
            plan_type=results[0]
            return plan_type
        except Exception as e:
            return "Server error: "+str(e)

def change_plan(email,plan_name):
        try:
            cur=get_db().execute("update users set plan_type=? where email=?",(plan_name,email))
            get_db().commit()
            return "Your plan has been successfully changed"
        except Exception as e:
            return "Server error: "+str(e)

    
