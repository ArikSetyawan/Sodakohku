from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
# from peewee import *

from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import pymongo, datetime, bson, requests, base64, time, random, string

# db = "Sodakohku.db"
# database = SqliteDatabase(db)

# class BaseModel(Model):
# 	class Meta:
# 		database=database

# class level_user(BaseModel):
# 	id = AutoField()
# 	nama_level = CharField(unique=True)

# class user(BaseModel):
# 	id = AutoField()
# 	id_level = ForeignKeyField(level_user)
# 	email = CharField(unique=True)
# 	username = CharField(unique=True)
# 	password = CharField()
#	saldo = IntegerField(default=0)
# 	email_verify = BooleanField(default=False)

# class transaksi(BaseModel):
# 	id = AutoField()
#	order_id = CharField(unique=True)
# 	id_user = ForeignKeyField(user)
# 	donatur = CharField()
# 	pesan = TextField()
# 	nominal = IntegerField()
# 	email = CharField()
# 	payment_method = CharField()
# 	payment_confirm = BooleanField(default=False)
# 	waktu_transaksi = DateTimeField()
# 	waktu_payment = DateTimeField(null=True)
# 	transaction_id = CharField(unique=True)
#	va = CharField()


# def create_tables():
# 	with database:
# 		database.create_tables([level_user,user])


app = Flask(__name__)
api = Api(app)
app.config['MONGO_URI'] = "mongodb://localhost:27017/Sodakohku" 
mongo = PyMongo(app)

# Payment Gateway Midtrans
app.config['CLIENT_KEY'] = "SB-Mid-client-Om38rLxsnGsMmu7V"
app.config['SERVER_KEY'] = "SB-Mid-server-LHqFToQlQDGPCJ2nJH66Mcyu"

class Resource_Index(Resource):
	def get(self):
		return jsonify({"hasil":"Berhasil Membuat Api"})

class resource_level_user(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id_level',type=int,help="id_level, must int")
		args = parser.parse_args()
		if args['id_level'] is None:
			data_level = []
			# query_level_user = level_user.select()
			query_level_user = mongo.db.level_user.find()
			for i in query_level_user:
				data = {}
				data['id'] = str(i['_id'])
				data['nama_level'] = i['nama_level']
				data_level.append(data)
			return jsonify({'status':"success",'data':data_level})
		else:
			try:
				data_level_user = level_user.get(level_user.id == args['id_level'])
				data_level = {}
				data_level['id'] = data_level_user.id
				data_level['nama_level'] = data_level_user.nama_level
				return jsonify({'status':"success",'data':data_level})
			except DoesNotExists:
				return jsonify({"status":"Gagal","message":"Data not found"})

	def post(self):
		try:
			data_json = request.json
			nama_level = str(data_json['nama_level'])

			level_user = mongo.db.level_user.insert({"nama_level":nama_level})
			return jsonify({"result":"success","message":"Berhasil dibuat"})
		except pymongo.errors.DuplicateKeyError as e:
			return jsonify({"status":"error",'message':str(e)})
		except KeyError:
			return jsonify({"status":"Invalid Key"})
		except TypeError:
			return jsonify({"status":"nama_level required"})

	def put(self):
		try:
			data_json = request.json
			id_level = str(data_json['id_level'])
			nama_level = str(data_json['nama_level'])

			update_level_user = mongo.db.level_user.update({"_id":ObjectId(id_level)},{"$set":{"nama_level":nama_level}})

			return jsonify({'status':'success','message':"level_user Berhasil diupdate"})
		except bson.errors.InvalidId:
			return jsonify({"status":"error",'message':"InvalidId"})
		except pymongo.errors.DuplicateKeyError as e:
			return jsonify({"status":"error",'message':str(e)})
		except KeyError:
			return jsonify({"status":"error","message":"Invalid Key"})
		except TypeError:
			return jsonify({"status":"error","message":"nama_level required"})

	def delete(self):
		try:
			parser = reqparse.RequestParser()
			parser.add_argument('id_level',type=str,required=True,help='id_level,must_str,required')	
			args = parser.parse_args()

			delete_level_user = mongo.db.level_user.remove({'_id':ObjectId(args['id_level'])})
			return jsonify({"status":"success",'message':"level user deleted"})
		except bson.errors.InvalidId:
			return jsonify({"status":"error",'message':"InvalidId"})

class resource_user(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id_user',type=str,help='id_user,must_str')
		args = parser.parse_args()

		if args['id_user'] is None:
			try:
				data_user = []
				query_user = mongo.db.user.find()
				for i in query_user:
					data = {}
					data['id_user'] = str(i['_id'])
					data['id_level'] = str(i['id_level'])
					query_level_user = mongo.db.level_user.find_one({'_id':ObjectId(i['id_level'])})
					if query_level_user is not None:
						data['nama_level'] = query_level_user['nama_level']
					else:
						pass
					data['email'] = i['email']
					data['username'] = i['username']
					data['password'] = i['password']
					data['saldo'] = i['saldo']
					data['email_verify'] = i['email_verify']
					data_user.append(data)
				return jsonify({"status":"success",'data':data_user})
			except bson.errors.InvalidId:
				return jsonify({"status":"error",'message':"InvalidId"})
		else:
			try:
				query_user = mongo.db.user.find_one({'_id':ObjectId(args['id_user'])})
				if query_user is not None:
					data_user = {}
					data_user['id_user'] = str(query_user['_id'])
					data_user['id_level'] = str(query_user['id_level'])
					query_level_user = mongo.db.level_user.find_one({'_id':ObjectId(query_user['id_level'])})
					if query_level_user is not None:
						data_user['nama_level'] = query_level_user['nama_level']
					else:
						pass
					data_user['email'] = query_user['email']
					data_user['username'] = query_user['username']
					data_user['password'] = query_user['password']
					data_user['saldo'] = query_user['saldo']
					data_user['email_verify'] = query_user['email_verify']
					return jsonify({'status':"success",'data':data_user})
				return jsonify({"status":"error","message":"user not found"})
			except bson.errors.InvalidId:
				return jsonify({"status":"error",'message':"InvalidId"})

	def post(self):
		try:
			data = request.json
			
			id_level = str(data['id_level'])
			email = str(data['email'])
			username = str(data['username'])
			password = str(data['password'])
			saldo = 0
			email_verify = False

			cek_id_level = mongo.db.level_user.find_one({'_id':ObjectId(id_level)})
			if cek_id_level is not None:
				user = mongo.db.user.insert({"id_level":id_level,"email":email,"username":username,"password":password,"saldo":saldo,"email_verify":email_verify})
				return jsonify({"status":"success", 'message':"user created"})
			else:
				return jsonify({"status":"error","message":"level_user not found"})
		except bson.errors.InvalidId:
			return jsonify({"status":"error",'message':"InvalidId"})
		except pymongo.errors.DuplicateKeyError as e:
			return jsonify({"status":"error",'message':str(e)})
		except KeyError:
			return jsonify({"status":"error","message":"Invalid Key"})
		except TypeError:
			return jsonify({"status":"error","message":"More Data required"})

	def put(self):
		try:
			data = request.json

			id_user = str(data['id_user'])
			username = str(data['username'])
			password = str(data['password'])

			user = mongo.db.user.update({'_id':ObjectId(id_user)},{"$set":{"username":username,'password':password}})
			return jsonify({"status":"success","message":"User Updated"})

		except bson.errors.InvalidId:
			return jsonify({"status":"error",'message':"InvalidId"})
		except pymongo.errors.DuplicateKeyError as e:
			return jsonify({"status":"error",'message':str(e)})
		except KeyError:
			return jsonify({"status":"error","message":"Invalid Key"})
		except TypeError:
			return jsonify({"status":"error","message":"More Data required"})

	def delete(self):
		try:
			parser = reqparse.RequestParser()
			parser.add_argument('id_user',type=str,required=True,help="id_user,must Str, required")
			args = parser.parse_args()

			user = mongo.db.user.remove({'_id':ObjectId(args['id_user'])})

			return jsonify({"status":"success","message":"user deleted"})
		except bson.errors.InvalidId:
			return jsonify({"status":"error",'message':"InvalidId"})

class resource_Verify_email(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id_user',type=str,required=True,help='id_user, must_str, required')
		args = parser.parse_args()
		try:
			cek_user = mongo.db.user.find_one({"_id":ObjectId(args['id_user'])})
			if cek_user is not None:
				if cek_user['email_verify'] is False:
					verify_user = mongo.db.user.update({"_id":ObjectId(args['id_user'])},{"$set":{"email_verify":True}})
					return jsonify({"status":"success",'message':"User verified"})
				else:
					return jsonify({"status":"error",'message':'user already verified'})
			else:
				return jsonify({"status":"error","message":"User not found"})
		except bson.errors.InvalidId:
				return jsonify({"status":"error",'message':"InvalidId"})

class resource_transaksi(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id_user',type=str, help='id_user, must str')
		args = parser.parse_args()

		if args['id_user'] is None:
			data_transaksi = []
			query_all_transaksi = mongo.db.transaksi.find()
			for i in query_all_transaksi:
				data = {}
				data['id'] = str(i['_id'])
				data['id_user'] = i['id_user']
				data['donatur'] = i['donatur']
				data['pesan'] = i['pesan']
				data['nominal'] = i['nominal']
				data['email'] = i['email']
				data['payment_confirm'] = i['payment_confirm']
				data['waktu_transaksi'] = i['waktu_transaksi']
				data['waktu_payment'] = i['waktu_payment']
				data['transaction_id'] = i['transaction_id']
				data['va'] = i['va']
				data['order_id'] = i['order_id']
				data_transaksi.append(data)
			return jsonify({"status":"success","data":data_transaksi})
		else:
			try:
				cek_user = mongo.db.user.find_one({'_id':ObjectId(args['id_user'])})
				if cek_user is not None:
					data_user = {}
					data_user['id_user'] = str(cek_user['_id'])
					data_user['id_level'] = str(cek_user['id_level'])
					query_level_user = mongo.db.level_user.find_one({'_id':ObjectId(cek_user['id_level'])})
					if query_level_user is not None:
						data_user['nama_level'] = query_level_user['nama_level']
					else:
						pass
					data_user['email'] = cek_user['email']
					data_user['username'] = cek_user['username']
					data_user['password'] = cek_user['password']
					data_user['saldo'] = cek_user['saldo']
					data_user['email_verify'] = cek_user['email_verify']

					data_transaksi = []
					query_traksaksi = mongo.db.transaksi.find({"id_user":args['id_user']})
					for i in query_traksaksi:
						data = {}
						data['id'] = str(i['_id'])
						data['id_user'] = i['id_user']
						data['donatur'] = i['donatur']
						data['pesan'] = i['pesan']
						data['nominal'] = i['nominal']
						data['email'] = i['email']
						data['payment_confirm'] = i['payment_confirm']
						data['waktu_transaksi'] = i['waktu_transaksi']
						data['waktu_payment'] = i['waktu_payment']
						data['transaction_id'] = i['transaction_id']
						data['va'] = i['va']
						data['order_id'] = i['order_id']
						data_transaksi.append(data)
					return jsonify({"status":"success","data":{"user":data_user,"transactions":data_transaksi}})
				else:
					return jsonify({"status":"error","message":"User Not Found"})
			except bson.errors.InvalidId:
				return jsonify({"status":"error",'message':"InvalidId"})

	def post(self):
		try:
			data = request.json

			id_user = str(data['id_user'])
			donatur = str(data['donatur'])
			pesan = str(data['pesan'])
			nominal = int(data['nominal'])
			email = str(data['email'])
			payment_confirm = False
			waktu_transaksi = datetime.datetime.now()
			waktu_payment = None
			transaction_id = None
			va = None
			order_id = 'TRX'+''.join(random.choice(string.digits) for _ in range(14))

			cek_user = mongo.db.user.find_one({"_id":ObjectId(id_user)})
			if cek_user is not None:


				url_inquiry = "https://api.sandbox.midtrans.com/v2/charge"
				headers = {
					"Accept":"application/json",
					"Content-Type":"application/json",
					"Authorization": "Basic {}".format(base64.b64encode(app.config['SERVER_KEY'].encode("UTF-8")).decode("UTF-8"))
				}
				json = {
					"payment_type":"bank_transfer",
					"transaction_details":{
						"order_id":order_id,
						"gross_amount":nominal
					},
					"bank_transfer":{
						"bank":"bca"
					},
					"customer_details": {
						"email":email,
						"first_name":donatur
					}
				}
				req = requests.post(url_inquiry,headers=headers,json=json)
				if req.status_code == 200:
					if req.json()['status_code'] == '201':
						req = req.json()
						transaction_id = req['transaction_id']
						va = req['va_numbers'][0]['va_number']
						
						transaksi = mongo.db.transaksi.insert(
							{
								"id_user":id_user,
								"donatur":donatur,
								"pesan":pesan,
								"nominal":nominal,
								"email":email,
								"payment_confirm":payment_confirm,
								"waktu_transaksi":waktu_transaksi,
								"waktu_payment":waktu_payment,
								"transaction_id":transaction_id,
								"va":va,
								"order_id":order_id
							}
						)

						return jsonify({"status":"success","message":"Transaksi {} Berhasil Dibuat. Silahkan Transfer ke Nomer Rekening : {}".format(order_id,va)})
					else:
						return jsonify({"status":"error","message":"something Wrong"})
				else:
					return jsonify({"status":"error","message":"Payment Gateway Error"})
			else:
				return jsonify({"status":"error","message":"User Not Found"})
		except bson.errors.InvalidId:
			return jsonify({"status":"error",'message':"InvalidId"})
		except pymongo.errors.DuplicateKeyError as e:
			return jsonify({"status":"error",'message':str(e)})
		except KeyError:
			return jsonify({"status":"error","message":"Invalid Key"})
		except TypeError:
			return jsonify({"status":"error","message":"More Data required"})
		
class Resource_Notification_Callback(Resource):
	def post(self):
		try:
			data = request.json
			print(data)
			return "oke"
		except KeyError:
			return jsonify({"status":"error","message":"Invalid Key"})
		except TypeError:
			return jsonify({"status":"error","message":"More Data required"})

api.add_resource(Resource_Index, '/api/index/')
api.add_resource(resource_level_user, '/api/level_user/')
api.add_resource(resource_user, '/api/user/')
api.add_resource(resource_Verify_email, '/api/email-verification/')
api.add_resource(resource_transaksi, '/api/transaction/')
api.add_resource(Resource_Notification_Callback, '/api/notification-callback/')

if __name__ == '__main__':
	# create_tables()
	app.run(debug=True)