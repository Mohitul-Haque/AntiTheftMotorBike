from flask import Flask
from flask import render_template,redirect,url_for,session,request,abort
from pymongo import MongoClient
from datetime import datetime
import pygal
import time
#ts = time.time()
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

##################### ADMIN HOME ####################

@app.route('/home')
def home():
    if 'user' and 'pass' in session:    
        return render_template('dashboard.html')  
    else:
        return redirect('/login')         

@app.route('/custom')
def custom():
    if 'user' and 'pass' in session:
        return render_template('custom_phone_msg.html')  
    else:
        return redirect('/login')  

@app.route('/custom_ststus', methods = ['POST','GET'])
def custom_status():
    if 'user' and 'pass' in session:
        if(request.method == 'POST'):
             on_status = request.form.get("status_on")
             off_status = request.form.get("status_off")
             phone_number = request.form.get("phonenumber")
             db.custom_status.update(
                 {"id":1},
                 {"$set": { 
                    "status_on":on_status,
                    "status_off":off_status,
                    "phonenumber":phone_number 
                    }
                 },multi=True)            
             return redirect('/custom')  
    else:
        return redirect('/login')   

################# BIKE CONTROL OPERATION ##################
def get_bike_custom_status(db):
     return db.custom_status.find_one({"id":1})


def get_bike_info(db):
     bike_current_status = db.bike_info.find_one(sort=[("_id", -1)])
     return bike_current_status


db = get_db()
custom_status = get_bike_custom_status(db)


@app.route('/bike-control')
def control():
    
        if 'user' and 'pass' in session:
            custom_status = get_bike_custom_status(db)
            bike_current_status = get_bike_info(db)            
            if(bike_current_status == None):
                last = 'none'
                time = 'none'
            else:    
                last = bike_current_status['status']
                time = bike_current_status['created']
            return render_template(
                'bike_control.html',
                last = last,
                status_on = custom_status['status_on'],
                status_off = custom_status['status_off'],
                time = time   
            )     

@app.route('/bike-on', methods = ['GET'])
def bike_on():
    db = get_db()
    custom_status = get_bike_custom_status(db)    
    if 'user' and 'pass' in session:
        if(request.method == 'GET'):
             status = request.args.get("status")             
             if(status == custom_status['status_on']):                
                db.bike_info.insert({
                    "status": status,
                    "created": datetime.now()
                    })             
                return redirect('/bike-control')   

@app.route('/bike-off')
def bike_off():
    db = get_db()
    custom_status = get_bike_custom_status(db)
    if 'user' and 'pass' in session:
        if(request.method == 'GET'):
             status = request.args.get("status")             
             if(status == custom_status['status_off']):
                db.bike_info.insert({
                    "status": status,
                    "created": datetime.now()
                    })                
                return redirect('/bike-control')   

##################### LOGOUT ################
@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('user', None)
   session.pop('pass',None)
   return redirect(url_for('login'))
         
################# <GRAPH> ############

def get_bike_on_info(db):
     time = db.bike_info.find()
     f=[]
     for result in time:
         a=result['created'].strftime('%S')
         #print(a) 
         #for i in result:
         f.append(int(a))
         print(f)
         #print(result['created'].strftime('%H:%M:%S'))


@app.route('/pygalexample/')
def pygalexample():
    try:
        graph = pygal.Bar()
        graph.title = '% History of ON and OFF over time.'
        datetimequery = db.bike_info.find()
        dur=[]
        graph.x_labels=[]
        for result in datetimequery:
            dates=result['created'].strftime('%Y-%m-%d')
            times=result['created'].strftime('%S')
            graph.x_labels.append(dates) 
            dur.append(int(times)) 
            graph.add('ON', dur)      
        #graph.x_labels = ['2017-02-26','2017-02-26','2017-02-26','2017-02-26','2017-02-26']
        #graph.add('OFF', [15, 30, 40, 50, 10])
        #graph.add('ON',  [15, 30, 40, 50, 10])        
        
        graph_data = graph.render_data_uri()
        return render_template("graphing.html", graph_data = graph_data)
    except Exception as e:
        return(str(e))
######################################

if __name__ == "__main__":
    db = get_db()    
    add_admin_info(db)
    get_admin_info(db)
    get_bike_on_info(db)
    #custom_status = get_bike_custom_status(db)    
    app.run(debug=True)   