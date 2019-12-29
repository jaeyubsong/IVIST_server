import os
import functools
from flask import Flask, flash, session, redirect, url_for, request, render_template, current_app, jsonify, send_file
from pymongo import MongoClient
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from flask_restplus import Api, Resource, fields
# from api import get_scan_result

import json
import logging


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
api = Api(app=app)
ns = api.namespace('vbs', description='design vbs web')

client = MongoClient('127.0.0.1', 27017)
db = client.testdb
col = db.allFrames_final

data_dir = '../ir.nist.gov/tv2019/V3C1/V3C1.webm.videos.shots/'

def priority_cmp(a, b):
  if a['checked'] == True:
    return-1
  else:
    return 1

@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
@ns.route("/")
class indexClass(Resource):
  def post(self):
    _items = col.find()
    items = [item for item in _items]
    #return render_template('index.html', items=items)
    return current_app.logger.info(items)

@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
@ns.route("/new")
#@ns.doc(params={'name': 'name', 'description': 'description'})
class newClass(Resource):
  def post(self):
    item_doc = { '_id': '', 'Text': '' }
    #name = request.form.to_dict("name")
    #current_app.logger.info(name)
    #description = request.form.to_dict("description")
    #"current_app.logger.info(description)
    #item_doc = { 'name': name, 'description': description }
    item_doc = request.form.to_dict()
    current_app.logger.info(item_doc)
    print("Add Object : ", item_doc)
    col.insert_one(item_doc)
    #return redirect(url_for('index'))
    return "Add Successfully" 

@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
@ns.route("/delete")
class deleteClass(Resource):
  def post(self):
    name_to_delete = { '_id': '' }
    name_to_delete = request.form.to_dict()
    print("Delete Object : ", name_to_delete)
    current_app.logger.info(name_to_delete)
    col.remove(name_to_delete)

    #return redirect('/')
    return "Delete Successfully" 
 
@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
@ns.route("/getData")
class getDataClass(Resource):
  def post(self):
    current_app.logger.info("getData called with data")
    _items = col.find({},{ "_id": 0, "Text": 1 })
    items = [item for item in _items]
    returnList = {"hits": []}
    returnList["hits"] = items
#    current_app.logger.info(items)
#    current_app.logger.info(json.dumps(items))
#    current_app.logger.info(jsonify(items))
#    current_app.logger.info(returnList)
    response = jsonify(returnList)
    #response.headers.add('Access-Control-Allow-Origin', '*')
    return response 

@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
@ns.route("/upload")
class fileUpload(Resource):
  def post(self):
    toUpload = request.files['toUpload']
    current_app.logger.info(toUpload.filename)
    toUpload.save(secure_filename(toUpload.filename))
    
    #read_data = data.read()
    #stored = fs.put(read_data, filename=str(toUpload.filename))
    #return {"status": "New image added", "name": list_of_names[id_doc[_id]]}
    #return 'upload successfully'
    #return send_file(toUpload.filename)
    return toUpload.filename
   
@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization']) 
@ns.route("/query")
class fileQuery(Resource):
  def post(self):
    current_app.logger.info("Called query")
    data = request.json
    data_list = data['myData']
    query_text_list = []
    current_app.logger.info(request.json)

    # For now, everything is in $OR
    current_app.logger.info('Finding')
    query = []
    high_priority = []
    low_priority = []
    cur_cond = {}
    for item in data_list:
      if item['type'] == 'object':
        cur_cond = {'object': {
          '$elemMatch': {
            'label': item['object']
          }
        }}
      elif item['type'] == 'text':
        cur_cond = {'text': item['text']}
      elif item['type'] == 'color':
        cur_cond = {'color': item['color']}
      elif item['type'] == 'sentence':
        current_app.logger.info('This is a sentence')
        os.system("bash implement.sh"+item['sentence'])

        with open('/home/ivy/IVIST_server/flask-backend/result_idx.txt', 'r') as scan_result_text:
          order_array = [line.strip() for line in scan_result_text]

        # order_array, scan_dict = get_scan_result(item['sentence'])
        
        # x = col.find({'$or': scan_dict})
        x = col.aggregate([
          {
            '$match': { 
              'scanId': {
                '$in': order_array
              }
            }
          },
          {
            '$addFields': {
              '_order': {
                '$indexOfArray':[order_array, "$scanId"]
              }
            }
          },
          {
            '$sort': {
              '_order': 1
            }
          },
          {"$limit": 1000}
        ])
        doc_list = []
        for doc in x:
          doc_list.append(doc)
        current_app.logger.info('Result is')
        current_app.logger.info(doc_list)
        
    
        returnList = jsonify(doc_list)
        return returnList
        

      query.append(cur_cond)
      if item['checked'] == True:
        high_priority.append(cur_cond)
      elif item['checked'] == False:
        low_priority.append(cur_cond)
      

    current_app.logger.info('Before OR and query is:')
    current_app.logger.info(query)
    # x = col.find({'$or': query})
    x = col.aggregate([
      {
        '$match': { 
          '$and': query
        }
      },
      # {
      #   '$addFields': {
      #     "sortField": {
      #       "$cond": {
      #         "if": {
      #           "$or": high_priority
      #         }, "then": 1,
      #         "else": 2
      #       }
      #     }
      #   }
      # },
      # {"$sort": {"sortField": 1}},
      {"$limit": 1000}
    ])


    current_app.logger.info('Finished finding')

    # current_app.logger.info(doc_list)
    doc_list = []
    for doc in x:
      del doc['_id']
      doc_list.append(doc)
    

    current_app.logger.info(doc_list[0])
    # doc_list = list(set(doc_list))
    current_app.logger.info('Inside high_priority')
    current_app.logger.info(high_priority)
    current_app.logger.info('Inside low_priority')
    current_app.logger.info(low_priority)
    # for found in doc_list:
    #     current_app.logger.info(found)
    
    returnList = jsonify(doc_list)
    return returnList


if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
