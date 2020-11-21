from flask import Flask, render_template, redirect, session,request,jsonify,send_file
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField
import db
import time
import os
import math

app = Flask(__name__)
app.config['SECRET_KEY'] = "find@me1290"
plans={"free":500,"pro":1000,"gold":5000,"platinum":10000}

class LoginForm(FlaskForm):
    email = StringField("Email")
    password = PasswordField("Password")
    submit = SubmitField("Log in")


class RegisterForm(FlaskForm):
    email = StringField("Email")
    password = PasswordField("Password")
    cpassword = PasswordField("Password")
    submit = SubmitField("Register")


@app.route("/authUser", methods=['POST'])
def authUser():
    form = LoginForm()
    email = str(form.email.data)
    password = str(form.password.data)
    status=db.login_user(email,password)
    if status:
        session['logged_in']=True
        session['email']=email
        return redirect('profile')
    else:
        error="Invalid email or password"
        form = LoginForm()
        regForm = RegisterForm()
        return render_template("members.html",error=error,form=form, rform=regForm)



@app.route("/registerUser", methods=['POST'])
def registerUser():
    status=""
    data = request.get_json()
    if data['password']!=data['cpassword']:
        status="password and confirm password does not match"
    else:
        status=db.register_user(data['email'],data['password'])
    time.sleep(1) ## to see the spinner loading add this or remove this for fast response
    try:
        base_dir=os.path.abspath(os.path.dirname(__file__))
        os.mkdir(os.path.join(base_dir,"static","files",data['email']))
    except Exception as e:
        print(str(e))
    response = {'status': status}
    return jsonify(response)

@app.route("/Logoutuser",methods=['POST'])
def logout():
    data=request.get_json()
    email=data['email']
    status="error"
    response={}
    if email==session['email']:
        session.pop('logged_in')
        session.pop('email')
        status="success"
        response["logged out"]=status
        return jsonify(response)
    response['logged out']=status
    return jsonify(response)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/members", methods=['POST', 'GET'])
def members():
    try:
        if session['logged_in']:
            return redirect('profile')
    except Exception as e:
        print("Some error")
    form = LoginForm()
    regForm = RegisterForm()
    error=""
    return render_template("members.html", form=form, rform=regForm,error=error)


@app.route("/pricing")
def pricing():
    return render_template("pricing.html")


@app.route("/profile")
def profile():
    if 'logged_in' in session:
        plan_name=db.get_plan_type(session['email'])
        plan_size=plans[plan_name]
        
        print(plan_size)
        try:
            base_dir=os.path.abspath(os.path.dirname(__file__))
            user_files=os.listdir(os.path.join(base_dir,"static","files",session['email']))
            user_files_size=[]
            utilized_size=0.0
            for items in user_files:
                size1=os.path.getsize(os.path.join(base_dir,"static","files",session['email'],items))
                size=str(round(size1/(1024*1024),3))
                user_files_size.append([items,size])
                utilized_size+=float(size)
        except Exception as e:
            print(str(e))
        session['utilized_size']=utilized_size
        session['plan_size']=plan_size
        plan_usage_percentage=math.ceil((int(utilized_size)/plan_size)*100)
        return render_template("profile.html",files=user_files_size,utilized_size=math.ceil(utilized_size),plan_usage_percentage=plan_usage_percentage,plan_size=plan_size,plan_name=plan_name)
    else:
        return redirect('members')

@app.route("/uploadFile",methods=['POST','GET'])
def upload_file():
    response={}
    try:
        base_dir=os.path.abspath(os.path.dirname(__file__))
        file_size=float(request.form.get('f_size'))
        file_size1=str(round(file_size/(1024*1024),3))
        f_size=float(file_size1)
        if (session['utilized_size']+f_size)>session['plan_size']:
            response['status']="Limit crossed"
            return jsonify(response)
        f=request.files['file']
        f.save(os.path.join(base_dir,"static","files",session['email'],f.filename))
        response={'status':''+str(f.filename)+str(" was succesfully uploaded")}
        return jsonify(response)
    except Exception as e:
        response['status']="Server error: "+str(e)
    return jsonify(response)

@app.route("/downloadfile/<filename>",methods=['GET','POST'])
def download_file(filename):
    base_dir=os.path.abspath(os.path.dirname(__file__))
    file_path=os.path.join(base_dir,"static","files",session['email'],filename)
    return send_file(file_path, as_attachment=True)

@app.route("/deletefile",methods=['GET','POST'])
def delete_file():
    data=request.get_json()
    file_name=data['filename']
    respone={"status":"An error occurred while deleting"}
    if 'logged_in' in session:
        base_dir=os.path.abspath(os.path.dirname(__file__))
        try:
            file_path=os.path.join(base_dir,"static","files",session['email'],file_name)
            os.remove(file_path)
            respone['status']=""+str(file_name)+" deleted successfully"
            return jsonify(respone)
        except Exception as e:
            respone['status']="Error "+str(e)
    return jsonify(respone)

@app.route("/changePlan",methods=['POST'])
def change_plan():
    response={"status":"error"}
    try:
        email=session['email']
        data=request.get_json()
        plan_name=data['plan_name']
        status=db.change_plan(email,plan_name)
        response['status']=status
        return jsonify(response)
    except Exception as e:
        response['status']=str(e)
    return jsonify(response)
    
    

    

  
