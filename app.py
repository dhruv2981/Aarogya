from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
from flask_mail import Mail , Message
import json
from authlib.integrations.flask_client import OAuth
from requests import Session

#flash is module to display messages
with open('config.json','r') as c:
    params = json.load(c)["params"]
 

local_server= True
app = Flask(__name__)
app.secret_key='dhruv'


# this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

# SMTP MAIL SERVER SETTINGS
#simple mail transfer protocol
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='587',
    MAIL_USE_SSL=False,
    MAIL_USE_TLS = True,
    #if mail is using ssl protocol    for establishing secure links between networked computers
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password'],
    MAIL_DEFAULT_SENDER=params["gmail-user"],
)
mail = Mail(app)
#configuration of mail with our app


@login_manager.user_loader
def load_user(user_id):
    return Auth.query.get(int(user_id))




# app.config['SQLALCHEMY_DATABASE_URI']='mysql://username:password@localhost/databas_table_name'
#no password by default
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/aarogya'
#aarogya is name of database table
db=SQLAlchemy(app)


#oauth=OAuth(app)
#google = oauth.register(
    #name = 'google',
    #access_token_url = 'https://accounts.google.com/o/oauth2/token',
   #access_token_params = None,
    #authorize_url = 'https://accounts.google.com/o/oauth2/auth',
    #authorize_params = None,
    #api_base_url = 'https://www.googleapis.com/oauth2/v1/',
    #userinfo_endpoint = 'https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    #client_kwargs = {'scope': 'openid email profile'},
    #extent of information google should provide to us scope)



# here we will create db models that is tables
#inheritance oops
class Activity(db.Model):
    tid=db.Column(db.Integer,primary_key=True)
    pid=db.Column(db.Integer)
    email=db.Column(db.String(80))
    name=db.Column(db.String(80))
    action=db.Column(db.String(80))
    timestamp=db.Column(db.String(80))
#we are inheriting from modal class in sqlalchemy


class Testing(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(80))
    email=db.Column(db.String(80))

class Auth(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(80))
    email=db.Column(db.String(80),unique=True)
    password=db.Column(db.String(700))


class Patients(db.Model):
    patient_id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(80))
    name=db.Column(db.String(80))
    gender=db.Column(db.String(80))
    slot=db.Column(db.String(80))
    disease=db.Column(db.String(80))
    
    #by default nullable =true it(false) means if following fields are left null sql query would not be executed 
    date=db.Column(db.String(80),nullable=False)
    department=db.Column(db.String(80))
    phone_number=db.Column(db.String(13))

class Testin(db.Model):
    identity=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(80))
    

class Dummy(db.Model):
    did=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(80))
    doctor_name=db.Column(db.String(80))
    dept=db.Column(db.String(80))



class Search(db.Model):
    dis=db.Column(db.String(80),primary_key=True)
    symptoms=db.Column(db.String(200))
    medicines=db.Column(db.String(200))

    




# here we will pass endpoints and run the fuction
@app.route('/')
def home():
    
    return render_template('home.html')
#render templates take string as input

#kept just for checking our database connection is ok    
@app.route('/dbtest')
def test():
    try:
        Testin.query.all()
        return 'Connection intact'
    except:
        return 'Connection is intact'





@app.route('/doctors',methods=['POST','GET'])
def doctors():

    if request.method=="POST":

        email=request.form.get('email')
        doctorname=request.form.get('doctorname')
        dept=request.form.get('dept')

        query=db.engine.execute(f"INSERT INTO `doctors` (`email`,`doctorname`,`dept`) VALUES ('{email}','{doctorname}','{dept}')")
        flash("Information is Stored","primary")

    return render_template('doctor.html')
#flash(message,categories) message is compulsory categories is optional







#two main request methods we are using get,post by default get method is called

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == "POST":
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        auth=Auth.query.filter_by(email=email).first()
        if auth:
            flash("Email Already Exist","warning")
            return render_template('/signup.html')
        passcode=generate_password_hash(password)

        new_auth=db.engine.execute(f"INSERT INTO `auth` (`username`,`email`,`password`) VALUES ('{username}','{email}','{passcode}')")

       
        flash("Signup Succes\n Please Login","info")
        return render_template('login.html')

          

    return render_template('signup.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        email=request.form.get('email')
        password=request.form.get('password')
        auth=Auth.query.filter_by(email=email).first()

        if auth and check_password_hash(auth.password,password):
            login_user(auth)
            flash("Login Success","info")
            return redirect(url_for('home'))
        else:
            flash("invalid credentials","info")
            return render_template('login.html')    

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))


@app.route('/search',methods=['POST','GET'])

def search():
    if request.method=="POST":
        query=request.form.get('search')
        disease=Search.query.filter_by(dis=query).first()
        give=db.engine.execute(f"SELECT * FROM `search` WHERE dis='{query}'")
        if disease:
            return render_template('search.html',give=give)
            
        else:

            flash("No Information Available","info")
            return render_template('home.html')
    return render_template('home.html')
#instead of filter_by you can use (filter here == will be used and it is based on verloaded objects)




@app.route('/patients',methods=['POST','GET'])
@login_required
def patient():
    doct=db.engine.execute("SELECT * FROM `doctors`")

    if request.method=="POST":
        email=request.form.get('email')
        name=request.form.get('name')
        gender=request.form.get('gender')
        slot=request.form.get('slot')
        disease=request.form.get('disease')
        date=request.form.get('date')
        department=request.form.get('dept')
        phone_number=request.form.get('number')
        
        query=db.engine.execute(f"INSERT INTO `patients` (`email`,`name`,`gender`,`slot`,`disease`,`date`,`department`,`phone_number`) VALUES ('{email}','{name}','{gender}','{slot}','{disease}','{date}','{department}','{phone_number}')")
        #query passed as string

# mail wala part
        
        msg = Message( sender = params['gmail-user'], recipients = [email])
        msg.body = f"Your booking is confirmed.\nThanks for choosing aarogya.\nThe details of your booking are-:\nName-:{name}\nSlot-:{slot}\n Date-:{date}\nDepartment-:{department}\nPhone no-:{phone_number}"
        mail.send(msg)
       
        flash("Booking Confirmed","info")


    return render_template('patient.html',doct=doct)

@app.route('/bookings')
@login_required
def bookings(): 
    em=current_user.email
    query=db.engine.execute(f"SELECT * FROM `patients` WHERE email='{em}'")
    return render_template('booking.html',query=query)
#to use python variable in sql query {variable}  should be used

@app.route("/update/<string:patient_id>",methods=['POST','GET'])
@login_required
def update(patient_id):
    posts=Patients.query.filter_by(patient_id=patient_id).first()
    if request.method=="POST":
        email=request.form.get('email')
        name=request.form.get('name')
        gender=request.form.get('gender')
        slot=request.form.get('slot')
        disease=request.form.get('disease')
        time=request.form.get('time')
        date=request.form.get('date')
        department=request.form.get('dept')
        phone_number=request.form.get('number')
         #in this keep care part in`` symbol is dtabse column name and rhs is variable defined using get method
        
        db.engine.execute(f"UPDATE `patients` SET `email` = '{email}', `name` = '{name} ', `gender` = '{gender}', `slot` = '{slot}', `disease` = '{disease}',       `time` = '{time}', `date` = '{date}', `department` = '{department}',              `phone_number` = '{phone_number}' WHERE `patients`.`patient_id` = {patient_id}   ")

        flash("Slot is updated","info")

        return redirect('/bookings')
    
       


    return render_template('update.html',posts=posts)
    #first posts is variable of python file


@app.route("/delete/<string:patient_id>",methods=['POST','GET'])
@login_required
def delete(patient_id):
    db.engine.execute(f"DELETE FROM `patients` WHERE `patients`.`patient_id`={patient_id}")
    flash("Slot Deleted Successful","info")
    return redirect('/bookings')
    
@app.route("/dummy")
def dummy():
    return render_template('dummy.html')


@app.route('/activity')
@login_required
def activity():
    
    posts=db.engine.execute("SELECT * FROM `activity`")
    return render_template('activity.html',posts=posts)








if __name__ == "__main__":
    app.run(debug=True)    


