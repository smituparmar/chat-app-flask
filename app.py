from flask import Flask,render_template,redirect,url_for,flash,jsonify,request
from wtform_fields import *
from models import *
from flask_login import LoginManager,login_user, current_user, login_required,logout_user
import datetime
import psycopg2
from psycopg2 import Error

#configure app
app = Flask(__name__)
app.secret_key = 'replace later'

#configure database
app.config['SQLALCHEMY_DATABASE_URI']='postgres://qwctqeinaukphp:40949257837d8d8009b7fc764fec0c61b8a85db2f0d6f789086d0e87555a465f@ec2-54-224-175-142.compute-1.amazonaws.com:5432/d25habt849s04d'

db= SQLAlchemy(app)

login=LoginManager(app)
login.init_app(app)

@login.user_loader
def load_user(id):
	return User.query.get(int(id))

#index page-home page
@app.route("/",methods=['GET','POST'])
def index():
	login_form = LoginForm()
	user_object =User.query.all()
	print(len(user_object))

	if login_form.validate_on_submit():
		user_object= User.query.filter_by(username=login_form.username.data).first()
		login_user(user_object)
		if current_user.is_authenticated:
			return redirect(url_for('chat'))
		return 'not logged in'
	return render_template("index.html",form=login_form)

#create chat from here
@app.route('/chat',methods=['GET','POST'])
def chat():
	chat_form=MessageScreen()
	if not current_user.is_authenticated:
		flash('Please login','danger')
		return redirect(url_for('login'))

	if chat_form.validate_on_submit():
		receiver= User.query.filter_by(username=chat_form.users.data).first()
		if not receiver:
			flash('enter valid receiver username','fail')
			return redirect(url_for('chat'))
		message = Messages(sender_id=current_user.id,receiver_id=receiver.id,time=datetime.datetime.now(),message=chat_form.message.data)
		db.session.add(message)
		db.session.commit()

		return redirect(url_for('chat'))
	return render_template('chat.html',form=chat_form)

#create group
@app.route('/create',methods=['GET','POST'])
def create_group():
	create_group_form=CreateGroupScreen()
	if create_group_form.validate_on_submit():
		groupname=create_group_form.groupname.data
		print(groupname)
		create_dynamic_table(groupname)
		group = Group(groupname=groupname)
		db.session.add(group)
		db.session.commit()

		return redirect(url_for('chat'))

	return render_template('create_group.html',form=create_group_form)

#group_chat has minor errors
@app.route('/group_chat',methods=['GET','POST'])
def group_chat():
	group_chat_form=GroupChat()
	if group_chat_form.validate_on_submit():
		groupname=group_chat_form.groupname.data
		msg=GroupMessages(sender_id=current_user.id,msg=group_chat_form.message.data)
		print(msg.query)
		msg.changeTableName(groupname)
		db.session.add(msg)
		db.session.commit()
		return redirect(url_for('group_chat'))
	return render_template('group_chat.html',form=group_chat_form)

#API-returns all users id and username in JSON
@app.route("/print",methods=['GET'])
def print_all():
	user_object =User.query.all()
	user_list=[]
	for i in user_object:
		user_dict=dict(id=i.id,username=i.username)
		user_list.append(user_dict)
	response=jsonify(user_list)
	print(response.data)
	return response

#API-for posting msg in database
@app.route("/create_chat/<user1>/<user2>/<msg>",methods=['POST'])
def create_chat(user1,user2,msg):
	data=[]
	if request.method=='POST':
		user_1=User.query.filter_by(username=user1).first()
		user_2=User.query.filter_by(username=user2).first()
		if(not user_1 or not user_2):
			response=jsonify({'message':'Enter valid username'})
			response.status_code=404
			return response
		user_1_id=str(user_1.id)
		user_2_id=str(user_2.id)
		message=Messages(sender_id=user_1_id,receiver_id=user_2_id,time=datetime.datetime.now(),message=msg)
		db.session.add(message)
		status=db.session.commit()
		response=jsonify({'message':'message added successfully'})
		return response


#API[GET]-give chat bertween user1 and user2 in JSON
@app.route("/chat/<user1>/<user2>",methods=['GET'])
def get_chat(user1,user2):
	data=[]
	if request.method=='GET':
		user_1=User.query.filter_by(username=user1).first()
		user_2=User.query.filter_by(username=user2).first()
		if(not user_1 or not user_2):
			response=jsonify(data)
			response.status_code=404
			return response
		user_1_id=str(user_1.id)
		user_2_id=str(user_2.id)
		#print(type(user_1_id),user_2_id)
		messages= Messages.query.all()
		for msg in messages:
			print(type(msg.sender_id),msg.receiver_id)
			if((msg.sender_id==user_1_id and msg.receiver_id==user_2_id) or 
				(msg.sender_id==user_2_id and msg.receiver_id==user_1_id)):
				msg_dict=dict(id=msg.id,sender=msg.sender_id,receiver=msg.receiver_id,time=msg.time,message=msg.message)
				#print(msg_dict)
				data.append(msg_dict)
		response = jsonify(data)
		response.status_code=202
		return response

#show chat in html using API
@app.route("/read_chat/<user1>/<user2>",methods=['GET'])
def read_chat(user1,user2):
	data=get_chat(user1,user2)
	print("status code is",data.status_code)
	if(data.status_code!=404):
		print(data.get_json())
		return render_template('read_chat.html',data=data.get_json(),user1=user1,user2=user2,status_code=data.status_code)
	else:
		return render_template('read_chat.html',data=data.get_json(),user1=user1,user2=user2,status_code=data.status_code)
	
#dynamic table creation for group chat
def create_dynamic_table(name):
	try:
		connection = psycopg2.connect(user = "qwctqeinaukphp",
    		password = "40949257837d8d8009b7fc764fec0c61b8a85db2f0d6f789086d0e87555a465f",
                                  host = "ec2-54-224-175-142.compute-1.amazonaws.com",
                                  port = "5432",
                                  database = "d25habt849s04d")
		cursor = connection.cursor()
		create_table_query = '''CREATE TABLE ''' + name +'''(ID SERIAL PRIMARY KEY     NOT NULL,
		sender_id           TEXT    NOT NULL,
		msg         Text NOT NULL); '''
		print(create_table_query)
		cursor.execute(create_table_query)
		connection.commit()
		print("Table created successfully in PostgreSQL ")
	except (Exception, psycopg2.DatabaseError) as error :
		print ("Error while creating PostgreSQL table", error)
	finally:
		if(connection):
			cursor.close()
			connection.close()
			print("PostgreSQL connection is closed")

if __name__ == '__main__':
	app.run(debug=True)
