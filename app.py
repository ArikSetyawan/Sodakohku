from flask import Flask, jsonify, request, render_template
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
# 	payment_detail = CharField(unique=True)
#	va = CharField()
# 	status = CharField()

# class payout(BaseModel):
# 	id = AutoField()
# 	payout_number = CharField(unique = True)
# 	id_user = ForeignKeyField(user)
# 	nominal = IntegerField()
# 	bank_name = CharField()
# 	nomor_rekening = IntegerField()
# 	nama_rekening = CharField()
# 	payout_request_time = DateTimeField()
# 	payout_complete_time = DateTimeField()
# 	payout_status = CharField(default='pending')
# 	payout_complete_status = BooleanField(default=False)

# def create_tables():
# 	with database:
# 		database.create_tables([level_user,user])


app = Flask(__name__)
api = Api(app)
# app.config['MONGO_URI'] = "mongodb://localhost:27017/Sodakohku"
app.config['MONGO_URI'] = "mongodb+srv://ariksetyawan:minuman1234@cluster0.xfhcs.mongodb.net/Sodakohku?retryWrites=true&w=majority"
mongo = PyMongo(app)

# Payment Gateway Midtrans
app.config['CLIENT_KEY'] = "SB-Mid-client-Om38rLxsnGsMmu7V"
app.config['SERVER_KEY'] = "SB-Mid-server-LHqFToQlQDGPCJ2nJH66Mcyu"


class resource_level_user(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id_level',type=str,help="id_level, must str")
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
			data_level_user = mongo.db.level_user.find_one({"_id":ObjectId(args['id_level'])})
			if data_level_user is not None:
				data_level = {}
				data_level['id'] = str(data_level_user['_id'])
				data_level['nama_level'] = data_level_user['nama_level']
				return jsonify({'status':"success",'data':data_level})
			else:
				return jsonify({"status":"error","message":"Level User Not Found"})

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
		parser.add_argument("username",type=str,help='username, must str')
		args = parser.parse_args()

		if args['id_user'] is not None and args['username'] is not None:
			return jsonify({"status":'error',"message":"Tolong Pilih Salah Satu Parameter"})
		elif args['id_user'] is None and args['username'] is None:
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
		elif args['id_user'] is not None:
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
		else:
			query_user = mongo.db.user.find_one({'username':ObjectId(args['username'])})
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
		parser.add_argument('order_id',type=str, help='order_id, must str')
		args = parser.parse_args()

		if args['id_user'] is not None and args['order_id'] is not None:
			return jsonify({"status":"error","message":"Tolong pilih salah satu parameter"})
		elif args['id_user'] is None and args['order_id'] is None:
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
				data['payment_method'] = i['payment_method']
				data['va'] = i['va']
				data['order_id'] = i['order_id']
				# get user/receiver
				query_user = mongo.db.user.find_one({'_id':ObjectId(i['id_user'])})
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
					data['receiver'] = data_user
				else:
					data["receiver"] = {}
				data_transaksi.append(data)
			return jsonify({"status":"success","data":data_transaksi})
		elif args['id_user'] is not None:
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
						data['payment_method'] = i['payment_method']
						data['va'] = i['va']
						data['order_id'] = i['order_id']
						data_transaksi.append(data)
					return jsonify({"status":"success","data":{"user":data_user,"transactions":data_transaksi}})
				else:
					return jsonify({"status":"error","message":"User Not Found"})
			except bson.errors.InvalidId:
				return jsonify({"status":"error",'message':"InvalidId"})
		else:
			# query transaksi by order_id
			query_transaksi = mongo.db.transaksi.find_one({"order_id":args['order_id']})
			if query_transaksi is not None:
				data_transaksi = {
					'id':str(query_transaksi['_id']),
					"id_user":query_transaksi['id_user'],
					"donatur":query_transaksi['donatur'],
					"pesan":query_transaksi['pesan'],
					"nominal":query_transaksi['nominal'],
					"email":query_transaksi['email'],
					"payment_confirm":query_transaksi['payment_confirm'],
					"waktu_transaksi":query_transaksi['waktu_transaksi'],
					"waktu_payment":query_transaksi['waktu_payment'],
					'payment_method' : query_transaksi['payment_method'],
					"va":query_transaksi['va'],
					"order_id":query_transaksi['order_id']
				}
				query_user = mongo.db.user.find_one({'_id':ObjectId(query_transaksi['id_user'])})
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
				else:
					data_user = {}
				return jsonify({"status":"success","data":{"user":data_user,"transaction":data_transaksi}})
			else:
				return jsonify({"status":"error","message":"transaction not found"})


	def post(self):
		try:
			data = request.json

			id_user = str(data['id_user'])
			donatur = str(data['donatur'])
			pesan = str(data['pesan'])
			nominal = int(data['nominal'])
			email = str(data['email'])
			payment_method = str(data['payment_method'])
			payment_confirm = False
			waktu_transaksi = None
			waktu_payment = None
			va = None
			order_id = 'TRX'+''.join(random.choice(string.digits) for _ in range(14))

			# available payment_method
			available_payment_method = ['bca','bni','permata']

			if nominal < 10000:
				return jsonify({"status":"error","message":"Nominal Terlalu Kecil"})

			if payment_method in available_payment_method:
				cek_user = mongo.db.user.find_one({"_id":ObjectId(id_user)})
				if cek_user is not None:


					url_inquiry = "https://api.sandbox.midtrans.com/v2/charge"
					headers = {
						"Accept":"application/json",
						"Content-Type":"application/json",
						"Authorization": "Basic {}".format(base64.b64encode(app.config['SERVER_KEY'].encode("UTF-8")).decode("UTF-8"))
					}
					if payment_method == 'bca':
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
					elif payment_method == 'permata':
						json = {
							"payment_type":"bank_transfer",
							"transaction_details":{
								"order_id":order_id,
								"gross_amount":nominal
							},
							"bank_transfer":{
								"bank":"permata",
								"permata":{
									"recipient_name":donatur
								}
							},
							"customer_details": {
								"email":email,
								"first_name":donatur
							}
						}
					elif payment_method == 'bni':
						json = {
							"payment_type":"bank_transfer",
							"transaction_details":{
								"order_id":order_id,
								"gross_amount":nominal
							},
							"bank_transfer":{
								"bank":"bni"
							},
							"customer_details": {
								"email":email,
								"first_name":donatur
							}
						}
					else:
						pass
					req = requests.post(url_inquiry,headers=headers,json=json)
					if req.status_code == 200:
						if req.json()['status_code'] == '201':
							req = req.json()
							if payment_method == 'permata':
								va = req['permata_va_number']
								waktu_transaksi = datetime.datetime.strptime(req['transaction_time'], '%Y-%m-%d %H:%M:%S')
							elif payment_method == 'bca':
								va = req['va_numbers'][0]['va_number']
								waktu_transaksi = datetime.datetime.strptime(req['transaction_time'], '%Y-%m-%d %H:%M:%S')
							elif payment_method == 'bni':
								va = req['va_numbers'][0]['va_number']
								waktu_transaksi = datetime.datetime.strptime(req['transaction_time'], '%Y-%m-%d %H:%M:%S')
							else:
								pass
							
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
									"payment_method":payment_method,
									"payment_detail":req,
									"va":va,
									"order_id":order_id,
									"status":"Pending"
								}
							)

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

							response = {
								"receiver":data_user,
								"donatur":donatur,
								"pesan":pesan,
								"nominal":nominal,
								"email":email,
								"waktu_transaksi":waktu_transaksi,
								"payment_method":payment_method,
								"va":va,
								"order_id":order_id,
								"status":"Pending"
							}

							return jsonify({"status":"success","data":response,"message":"Transaksi {} Berhasil Dibuat. Silahkan Transfer ke {} Nomer Rekening : {}".format(order_id,payment_method,va)})
						else:
							return jsonify({"status":"error","message":"something Wrong"})
					else:
						return jsonify({"status":"error","message":"Payment Gateway Error"})
				else:
					return jsonify({"status":"error","message":"User Not Found"})
			else:
				return jsonify({"status":"error","message":"Payment Method Not Found"})
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

			transaction_status = data['transaction_status']
			order_id = data['order_id']
			if transaction_status == "settlement":
				settlement_time =  datetime.datetime.strptime(data['settlement_time'], '%Y-%m-%d %H:%M:%S')
				update_status_transaksi = mongo.db.transaksi.update({'order_id':order_id},{"$set":{"status":"Complete","waktu_payment":settlement_time,"payment_confirm":True}})
				
				# get transaction
				query_transaksi = mongo.db.transaksi.find_one({'order_id':order_id})

				# get user
				query_user = mongo.db.user.find_one({'_id':ObjectId(query_transaksi['id_user'])})

				# update saldo user
				update_saldo = mongo.db.user.update({'_id':ObjectId(query_transaksi['id_user'])},{'$set':{'saldo':query_transaksi['nominal'] + query_user['saldo']}})

			elif transaction_status == "expire":
				update_status_transaksi = mongo.db.transaksi.update({'order_id':order_id},{"$set":{"status":transaction_status}})
			else:
				pass

			return "oke"
		except KeyError:
			return jsonify({"status":"error","message":"Invalid Key"})
		except TypeError:
			return jsonify({"status":"error","message":"More Data required"})

class Resource_payout(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id_user',type=str,help='id_user must str')
		parser.add_argument('payout_number', type=str, help='payout_number, must str')
		args = parser.parse_args()

		if args['id_user'] is not None and args['payout_number'] is not None:
			return jsonify({"status":"error",'message':'Tolong Pilih Salah satu parameter'})
		elif args['id_user'] is None and args['payout_number'] is None:
			data_payout = []
			query_all_payout = mongo.db.payout.find()
			for i in query_all_payout:
				data  = {}
				data['id'] = str(i['_id'])
				data['payout_number'] = i['payout_number']
				data['id_user'] = i['id_user']
				data['nominal'] = i['nominal']
				data['bank_name'] = i['bank_name']
				data['nomor_rekening'] = i['nomor_rekening']
				data['nama_rekening'] = i['nama_rekening']
				data['payout_request_time'] = i['payout_request_time']
				data['payout_complete_time'] = i['payout_complete_time']
				data['payout_status'] = i['payout_status']
				data['payout_complete_status'] = i['payout_complete_status']
				# get user
				query_user = mongo.db.user.find_one({'_id':ObjectId(i['id_user'])})
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
					data['user'] = data_user
				else:
					data["user"] = {}
				data_payout.append(data)
			return jsonify({"status":"success","data":data_payout})
		elif args['id_user'] is not None:
			try:
				# cek user
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

					data_payout = []
					query_payout = mongo.db.payout.find({'id_user':args['id_user']})
					for i in query_payout:
						data  = {}
						data['id'] = str(i['_id'])
						data['payout_number'] = i['payout_number']
						data['id_user'] = i['id_user']
						data['nominal'] = i['nominal']
						data['bank_name'] = i['bank_name']
						data['nomor_rekening'] = i['nomor_rekening']
						data['nama_rekening'] = i['nama_rekening']
						data['payout_request_time'] = i['payout_request_time']
						data['payout_complete_time'] = i['payout_complete_time']
						data['payout_status'] = i['payout_status']
						data['payout_complete_status'] = i['payout_complete_status']
						data_payout.append(data)
					return jsonify({"status":"success","data":{"payout":data_payout,"user":data_user}})
				else:
					return jsonify({"status":"errors","data":"User not Found"})
			except bson.errors.InvalidId:
				return jsonify({"status":"error",'message':"InvalidId"})
		else:
			# query payout
			query_payout = mongo.db.payout.find_one({'payout_number':args['payout_number']})
			if query_payout is not None:
				data_payout = {}
				data_payout['id'] = str(query_payout['_id'])
				data_payout['payout_number'] = query_payout['payout_number']
				data_payout['id_user'] = query_payout['id_user']
				data_payout['nominal'] = query_payout['nominal']
				data_payout['bank_name'] = query_payout['bank_name']
				data_payout['nomor_rekening'] = query_payout['nomor_rekening']
				data_payout['nama_rekening'] = query_payout['nama_rekening']
				data_payout['payout_request_time'] = query_payout['payout_request_time']
				data_payout['payout_complete_time'] = query_payout['payout_complete_time']
				data_payout['payout_status'] = query_payout['payout_status']
				data_payout['payout_complete_status'] = query_payout['payout_complete_status']
				
				query_user = mongo.db.user.find_one({'_id':ObjectId(query_payout['id_user'])})
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
				else:
					data_user = {}

				return jsonify({"status":"success","data":{"user":data_user,"payout":data_payout}})
			else:
				return jsonify({"status":"error","message":"payout not found"})

	def post(self):
		try:
			data = request.json
			payout_number = 'PAYOUT'+''.join(random.choice(string.digits) for _ in range(14))
			id_user = str(data['id_user'])
			nominal = int(data['nominal'])
			bank_name = str(data['bank_name'])
			nomor_rekening = int(data['nomor_rekening'])
			nama_rekening = str(data['nama_rekening'])
			payout_request_time = datetime.datetime.now()
			payout_complete_time = None
			payout_status = "pending"
			payout_complete_status = False

			# cek nominal lebih dari 100000
			if nominal < 100000:
				return jsonify({"status":"error","message":"Nominal Kurang"})

			# cek user dan saldo
			query_user = mongo.db.user.find_one({'_id':ObjectId(id_user)})
			if query_user is not None:
				if query_user['saldo'] >= nominal:
					# insert to db
					payout_data = {
						"payout_number":payout_number,
						"id_user":id_user,
						"nominal":nominal,
						"bank_name":bank_name,
						"nomor_rekening":nomor_rekening,
						"nama_rekening":nama_rekening,
						"payout_request_time":payout_request_time,
						"payout_complete_time":payout_complete_time,
						"payout_status":payout_status,
						"payout_complete_status":payout_complete_status
					}
					insert_payout = mongo.db.payout.insert(payout_data)
					# Update Saldo User
					update_saldo = mongo.db.user.update({"_id":ObjectId(id_user)},{"$set":{"saldo":query_user['saldo']-nominal}})

					response = {
						"payout_number":payout_number,
						"id_user":str(query_user['_id']),
						"nominal":nominal,
						"bank_name":bank_name,
						"nomor_rekening":nomor_rekening,
						"nama_rekening":nama_rekening,
						"payout_request_time":payout_request_time,
						"payout_complete_time":payout_complete_time,
						"payout_status":payout_status,
						"payout_complete_status":payout_complete_status
					}

					return jsonify({"status":"success","message":"Payout Berhasil","data":response})
				else:
					return jsonify({"status":"error","message":"Saldo Tidak Mencukupi"})
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

class Resource_payout_complete(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument("payout_number",type=str,required=True,help='payout_number, must str, required')
		args = parser.parse_args()

		cek_payout = mongo.db.payout.find_one({'payout_number':args['payout_number']})
		if cek_payout is not None:
			if cek_payout['payout_complete_status'] == False:
				update_payout = mongo.db.payout.update({"payout_number":args['payout_number']},{"$set":{"payout_complete_status":True,"payout_complete_time":datetime.datetime.now(),"payout_status":"Complete"}})
				get_payout_data = mongo.db.payout.find_one({'payout_number':args['payout_number']})
				data_payout = {
					"id":str(get_payout_data['_id']),
					"payout_number":get_payout_data['payout_number'],
					"id_user":get_payout_data['id_user'],
					"nominal":get_payout_data['nominal'],
					"bank_name":get_payout_data['bank_name'],
					"nomor_rekening":get_payout_data['nomor_rekening'],
					"nama_rekening":get_payout_data['nama_rekening'],
					"payout_request_time":get_payout_data['payout_request_time'],
					"payout_complete_time":get_payout_data['payout_complete_time'],
					"payout_status":get_payout_data['payout_status'],
					"payout_complete_status":get_payout_data['payout_complete_status']
				}
				return jsonify({"status":"success","message":"Payout Berhasil Diselesaikan","data":data_payout})
			else:
				return jsonify({"status":"error","message":"Payout Sudah Diselesaikan"})
		else:
			return jsonify({"status":"error","message":"payout_number not found"})

api.add_resource(resource_level_user, '/api/level_user/')
api.add_resource(resource_user, '/api/user/')
api.add_resource(resource_Verify_email, '/api/email-verification/')
api.add_resource(resource_transaksi, '/api/transaction/')
api.add_resource(Resource_Notification_Callback, '/api/notification-callback/')
api.add_resource(Resource_payout, '/api/payout/')
api.add_resource(Resource_payout_complete, "/api/mark-payout/")

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/docs/level-user/')
def docs_level_user():
	return render_template('level_user.html')

@app.route('/docs/user/')
def docs_user():
	return render_template('user.html')

@app.route('/docs/transaction/')
def docs_transaction():
	return render_template('transaction.html')

@app.route('/docs/payout/')
def docs_payout():
	return render_template('payout.html')

if __name__ == '__main__':
	# create_tables()
	app.run(debug=True, port=5001)