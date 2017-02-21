from flask import Flask
from flask import render_template,redirect,url_for,session,request,abort
from pymongo import MongoClient
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


############ DB CONFIG #############
def get_db():    
    uri = "mongodb://bike_admin:group_3@ds157499.mlab.com:57499/motorbike" 
    client = MongoClient(uri)
    db = client.motorbike
    return db 

def add_admin_info(db):
    a = get_admin_info(db)
    if(a==None):
        return db.admin_info.insert({
            "username": "Admin",
            "password": "123"
            }) 

def get_admin_info(db):
     return db.admin_info.find_one()

################### END DB CONFIG ##########

@app.route('/')

###################### LOGIN ###################

@app.route('/login')
def login(): 
    if 'user' and 'pass' in session:
        return redirect(url_for('home'))
    return render_template(
        'login.html'
    )
@app.route('/login_check', methods = ['POST','GET'])	
def login_check():
    #db = get_db()
    admin = get_admin_info(db)
    if 'user' and 'pass' in session:
        return redirect(url_for('home'))
    if(request.method == 'POST'):
        username = request.form['username']
        password = request.form['password']        
        if(username == admin['username'] and password == admin['password']):
            session['user']= username
            session['pass']= password
            return redirect(url_for('home'))
        else:
            return render_template(
                'login.html',
                 msg='Username or Password not matched! Please try again..'
            )                           
    elif(request.method == 'GET'):
        return redirect('/login')

########### ADMIN HOME ###########

@app.route('/home')
def home():
    if 'user' and 'pass' in session:
    #if(session['user']=='papel' and session['pass']=='123'):
        return render_template('dashboard.html')  
    else:
        return redirect('/login')         

@app.route('/bike-control')
def control():
    if 'user' and 'pass' in session:
        return render_template(
            'bike_control.html'       
        )

@app.route('/bike-on', methods = ['GET'])
def bike_on():
    if 'user' and 'pass' in session:
        if(request.method == 'GET'):
             if(request.args.get("status")=='ON'):
                return render_template(
                    'bike_control.html',
                    status='ON'                    
                )
             else:
                 return redirect('/bike-control')   
@app.route('/bike-off')
def bike_off():
    if 'user' and 'pass' in session:
        if(request.method == 'GET'):
             if(request.args.get("status")=='OFF'):
                return render_template(
                    'bike_control.html',
                    status='OFF'
                )
             else:
                 return redirect('/bike-control')   

@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('user', None)
   session.pop('pass',None)
   return redirect(url_for('login'))
         


if __name__ == "__main__":
    db = get_db()    
    add_admin_info(db)
    get_admin_info(db)    
    app.run(debug=True)   