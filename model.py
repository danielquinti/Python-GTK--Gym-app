# coding: utf-8

import pymongo
import base64
import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from gi.repository import Gtk, Gdk, GdkPixbuf
import gettext
import datetime


class Model:
	def set_transl(self,transl):
		_=transl.gettext

	def get_data(self):
		#client=MongoClient('localhost',5555,connectTimeoutMS=5,socketTimeoutMS=5,serverSelectionTimeoutMS=5)
		client=MongoClient(connectTimeoutMS=5000,socketTimeoutMS=5000,serverSelectionTimeoutMS=5000)
		database = client.workouts
		collection = database.workouts
		documents = collection.find()
		data = []
		for document in documents:
			workout_id = document['_id']
			workout_name = document['name']
			workout_date = document['date']
			workout_image = document['image']
			data.append([str(workout_name), str(workout_date), self.image_to_pixbuf(workout_id, workout_image), str(workout_id)])
		return data

	def image_to_pixbuf(self, workout_id, workout_image):
		if workout_id != "":
			os.chdir('images')
			if workout_image == "":
				pixbuf = GdkPixbuf.Pixbuf.new_from_file('image-missing.png').scale_simple(120, 90, GdkPixbuf.InterpType.BILINEAR)
				os.chdir('..')
				return pixbuf
			else:
				binary_image = base64.b64decode(workout_image)
				filename = str(workout_id) + ".jpg"
				with open(filename, 'wb') as f:
					f.write(binary_image)
				pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename).scale_simple(120, 90, GdkPixbuf.InterpType.BILINEAR)
				os.chdir('..')
				return pixbuf

	def workout_id_from_row(self,row):
		return row[3]

	def get_workout_data(self, workout_id):
		#client=MongoClient('localhost',5555,connectTimeoutMS=5,socketTimeoutMS=5,serverSelectionTimeoutMS=5)
		client=MongoClient(connectTimeoutMS=5000,socketTimeoutMS=5000,serverSelectionTimeoutMS=5000)
		database = client.workouts
		collection_workouts = database.workouts
		document = collection_workouts.find_one({'_id': ObjectId(workout_id)})
		exercises_from_workout = document['exercises']
		collection_of_exercises = database.exercises
		workout_data = []
		workout_id=document['_id']
		workout_name=document['name']
		for exercise in exercises_from_workout:
			exercise_data = []
			exercise_data.append(exercise[1])
			exercise_document = collection_of_exercises.find_one({'name': exercise[0]})
			if exercise_document is not None:
				for field in exercise_document:
					if field == 'image':
						exercise_data.append(self.image_to_pixbuf(exercise_document['_id'], exercise_document[field]))
					else:
						if field == 'description':
							description=exercise_document[field]
							if description=="":
								no_desc_text=_("No description available.")
								exercise_data.append(no_desc_text)							
							else:
								steps = str()
								for step in description:
									steps +=step + ' '
								exercise_data.append(steps)
						else:
							if field != '_id':
								exercise_data.append(exercise_document[field])
			else:
				exercise_data.append(exercise[0])
				exercise_data.append("")
				exercise_data.append(self.image_to_pixbuf("", ""))
				absent_exercise_text=_("This exercise is not in our database")
				exercise_data.append(absent_exercise_text)
			workout_data.append(exercise_data)
		return workout_data, workout_id,workout_name

	def delete_workout(self, workout_id):
		client=MongoClient(connectTimeoutMS=5000,socketTimeoutMS=5000,serverSelectionTimeoutMS=5000)
		database = client.workouts
		collection = database.workouts
		query = {"_id": ObjectId(workout_id)}
		collection.delete_one(query)

	def translate_date(self, data):
		date_str = data[1]
		format_str = '%d-%m-%Y'
		datetime_obj = datetime.datetime.strptime(date_str, format_str)
		data[1]=datetime_obj.strftime("%x")
		return data

	def get_doc(self, collection, key, value):
		client = MongoClient(
			connectTimeoutMS=5000, socketTimeoutMS=5000, serverSelectionTimeoutMS=5000)
		database = client.workouts
		collection = database.workouts
		return collection.find_one({key: ObjectId(value)})

	def switch_places(self, doc, starting_idx, target_idx):
		array = doc['exercises']
		if (starting_idx == 0 and target_idx < 0):
			target_idx = len(array)-1
		elif (starting_idx == len(array)-1 and target_idx == len(array)):
			target_idx = 0
		tmp = array[target_idx]
		array[target_idx] = array[starting_idx]
		array[starting_idx] = tmp
		tmp_doc = {'_id': doc['_id'],
				   'name': doc['name'],
				   'description': doc['description'],
				   'image': doc['image'],
				   'exercises': doc['exercises'],
				   'date': doc['date']}
		self.update_data(tmp_doc)
		return target_idx


	def update_data(self, doc):
		try:
			client = MongoClient(
				connectTimeoutMS=5000, socketTimeoutMS=5000, serverSelectionTimeoutMS=5000)
			database = client.workouts
			collection = database.workouts
			element = collection.find_one(doc['_id'])
			if collection is None:
				collection.insert_one(doc)
			else:
				client = MongoClient(
					connectTimeoutMS=5000, socketTimeoutMS=5000, serverSelectionTimeoutMS=5000)
				database = client.workouts
				collection = database.workouts
				query = {"_id": ObjectId(doc['_id'])}
				collection.delete_one(query)
				client = MongoClient(
					connectTimeoutMS=5000, socketTimeoutMS=5000, serverSelectionTimeoutMS=5000)
				database = client.workouts
				collection = database.workouts
				collection.insert_one(doc)
		except Exception as e:
			raise(e)
