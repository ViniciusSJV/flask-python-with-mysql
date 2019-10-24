from flask import Flask, render_template, request, json
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_teste'

mysql = MySQL(app)

@app.route("/login", methods=['GET'])
def login():
    return render_template("login.html", showConfirmPassWord = False)
		
@app.route('/sing_in', methods=['POST'])
def sing_in():
	name = request.form.get('name')
	password = request.form.get('password')
	return UserService().try_login_user(name, password)
	
@app.route("/confirm_password/<id_user>", methods=['GET'])
def confirm_password(id_user):
    return render_template("login.html", showConfirmPassWord = True, id = id_user)
	
@app.route('/confirm', methods=['POST'])
def confirm():
	newPassword = request.form.get('newPassword')
	confirmPassword = request.form.get('confirmPassword')
	idUser = request.form.get('idUser')
	
	return UserService().try_register_user(newPassword, confirmPassword, idUser)
	
@app.route("/main/<id>", methods=['GET'])
def main(id):
	return render_template("main.html", stores = StoreService().get_all_store(), user_name = UserService().get_name_user(id))

class UserService:

	@staticmethod
	def try_login_user(name, password):

		with Database() as data_base:
			data_base.execute("SELECT * FROM auth_user where username=%s and password=%s", (name, password))
			result = data_base.fetchone()
		
		if result is None:
			response = app.response_class(
				response=json.dumps('Nome ou senha incorretos'),
				status=403,
				mimetype='application/json'
			)
		else:
			id = str(result[0])
			password_change = result[3]
			
			if password_change == 0:
				response = app.response_class(
					response=json.dumps('/confirm_password/' + id),
					status=200,
					mimetype='application/json'
				)
			else:
				response = app.response_class(
					response=json.dumps('/main/' + id),
					status=200,
					mimetype='application/json'
				)
		return response	
		
	@staticmethod
	def try_register_user(newPassword, confirmPassword, idUser):	
		if newPassword == confirmPassword:
			
			with Database() as data_base:
				data_base.execute("UPDATE auth_user SET password=%s, password_change=1 where id=%s", (newPassword, idUser))
			
			response = app.response_class(
				response=json.dumps('/main/' + idUser),
				status=200,
				mimetype='application/json'
			)
		else:
			response = app.response_class(
				response=json.dumps('Senhas nao coincidem'),
				status=403,
				mimetype='application/json'
			)
		return response	
		
	@staticmethod
	def get_name_user(idUser):	
		
		with Database() as data_base:
			data_base.execute("SELECT username FROM auth_user where id=%s", (idUser))
			result = data_base.fetchone()
		
		return str(result[0])
		
	@staticmethod
	def get_all_manager(idUser):		
		response = list()
		
		with Database() as data_base:
			data_base.execute("SELECT * FROM auth_user where id!=%s", (idUser))
			result = data_base.fetchall()
		
		for row in result:
			response.append({
				'id': row[0],
				'name': row[2],
				'store_id': row[4] 
			})
			
		return response		
	
class StoreService:

	@staticmethod
	def get_all_store():
		response = list()
		
		with Database() as data_base:
			data_base.execute("SELECT * FROM store")
			result = data_base.fetchall()
		
		for row in result:
			response.append({
				'id': row[0],
				'name': row[1],
				'end': 'Rua: ' + str(row[3]) + ' ' + str(row[9]) + ' - ' + str(row[5]) + '/' + str(row[6]),
				'document': row[2] 
			})
			
		return response		
	
class Database:
	def __init__(self):
		self._conn = mysql.connection
		self._cursor = self._conn.cursor()
		
	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.commit()
		self.cursor.close()
		
	@property
	def connection(self):
		return self._conn

	@property
	def cursor(self):
		return self._cursor

	def commit(self):
		self.connection.commit()
	
	def execute(self, sql, params=None):
		self.cursor.execute(sql, params or ())

	def fetchall(self):
		return self.cursor.fetchall()

	def fetchone(self):
		return self.cursor.fetchone()

	def query(self, sql, params=None):
		self.cursor.execute(sql, params or ())
		return self.fetchall()