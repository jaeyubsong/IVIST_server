import os
import functools
from flask import Flask, flash, session, redirect, url_for, request, render_template, current_app, jsonify, send_file
from pymongo import MongoClient
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from flask_restplus import Api, Resource, fields
from api import get_scan_result
# import api
import json
import logging
import numpy as np
import time
import requests
import csv



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
        return -1
    else:
        return 1


def send_test(url_addr, contents):
    response = requests.post("%s" %(url_addr), data={'CONTENT':contents})
    return response


@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
@ns.route("/")
class indexClass(Resource):
    def post(self):
        _items = col.find()
        items = [item for item in _items]
        # return render_template('index.html', items=items)
        return current_app.logger.info(items)


@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
@ns.route("/new")
# @ns.doc(params={'name': 'name', 'description': 'description'})
class newClass(Resource):
    def post(self):
        item_doc = {'_id': '', 'Text': ''}
        # name = request.form.to_dict("name")
        # current_app.logger.info(name)
        # description = request.form.to_dict("description")
        # "current_app.logger.info(description)
        # item_doc = { 'name': name, 'description': description }
        item_doc = request.form.to_dict()
        current_app.logger.info(item_doc)
        print("Add Object : ", item_doc)
        col.insert_one(item_doc)
        # return redirect(url_for('index'))
        return "Add Successfully"


@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
@ns.route("/delete")
class deleteClass(Resource):
    def post(self):
        name_to_delete = {'_id': ''}
        name_to_delete = request.form.to_dict()
        print("Delete Object : ", name_to_delete)
        current_app.logger.info(name_to_delete)
        col.remove(name_to_delete)

        # return redirect('/')
        return "Delete Successfully"


@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
@ns.route("/getData")
class getDataClass(Resource):
    def post(self):
        current_app.logger.info("getData called with data")
        _items = col.find({}, {"_id": 0, "Text": 1})
        items = [item for item in _items]
        returnList = {"hits": []}
        returnList["hits"] = items
        #    current_app.logger.info(items)
        #    current_app.logger.info(json.dumps(items))
        #    current_app.logger.info(jsonify(items))
        #    current_app.logger.info(returnList)
        response = jsonify(returnList)
        # response.headers.add('Access-Control-Allow-Origin', '*')
        return response


@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
@ns.route("/upload")
class fileUpload(Resource):
    def post(self):
        toUpload = request.files['toUpload']
        current_app.logger.info(toUpload.filename)
        toUpload.save(secure_filename(toUpload.filename))

        # read_data = data.read()
        # stored = fs.put(read_data, filename=str(toUpload.filename))
        # return {"status": "New image added", "name": list_of_names[id_doc[_id]]}
        # return 'upload successfully'
        # return send_file(toUpload.filename)
        return toUpload.filename


@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
@ns.route("/query")
class fileQuery(Resource):
    def post(self):
        current_app.logger.info("Called query")
        data = request.json
        data_list = data['myData']
        current_app.logger.info('Data List')
        current_app.logger.info(data_list)
        query_text_list = []
        current_app.logger.info(request.json)

        # For now, everything is in $OR
        current_app.logger.info('Finding')
        query = []
        st_query = []
        high_priority = []
        high_priority_object = []
        low_priority = []
        low_priority_object = []
        cur_cond = {}
        st_cur_cond = {}
        for item in data_list:
            if item['type'] == 'object':
                if item['object'] == 'person':
                    cur_cond = {'object': {
                        '$elemMatch': {
                            'label': item['object'],
                            'score': {'$gte': 0.7}
                        }
                    }}
                else:
                    cur_cond = {'object': {
                        '$elemMatch': {
                            'label': item['object'],
                            'score': {'$gte': 0.4}
                        }
                    }}
                query.append(cur_cond)
            elif item['type'] == 'text':
                st_cur_cond = {'text': {
                    '$elemMatch': {
                        '$regex': item['text'],
                        '$options': 'i'
                    }
                }}
                st_query.append(st_cur_cond)
            elif item['type'] == 'color':
                cur_cond = {'color': item['color']}
                query.append(cur_cond)
            elif item['type'] == 'sentence':
                current_app.logger.info('This is a sentence')
                # order_array, scan_dict = get_scan_result(item['sentence'])
                item['sentence'] = '\"' + item['sentence'] + '\"'
                os.system("bash implement.sh " + item['sentence'])

                with open('/simpleFlaskApp/result_idx.tsv', 'r') as scan_result_text:
                    id_sim_list = [line.strip() for line in scan_result_text]

                current_app.logger.info('=======================================')
                current_app.logger.info(len(id_sim_list))

                result_list = []
                for i in range(len(id_sim_list)):
                    result_list.append({"scanIndex": int(id_sim_list[i].split('\t')[0]), "similarity": id_sim_list[i].split('\t')[1]})
                result_list = sorted(result_list, key=lambda x: x['similarity'], reverse=True)

                current_app.logger.info('=======================================')
                current_app.logger.info(len(result_list))

                # """ By loading tsv """
                # scan_dict = []
                # with open('/simpleFlaskApp/real_final.tsv', 'r') as tsv:
                #     t = csv.reader(tsv)
                #     for line in t:
                #         if line[0].split('\t')[0] == 'image_id':
                #             pass
                #         else:
                #             scan_dict.append(line[0].split('\t')[2])
                # current_app.logger.info(len(scan_dict))
                #
                # doc_list = []
                # for i in range(10):
                #     scanID_list = []
                #     for it in result_list[i*(len(result_list)//10):(i+1)*(len(result_list)//10)]:
                #         scanID_list.append(it['scanIndex'])
                #     current_app.logger.info('==============scanID_list==============')
                #     current_app.logger.info(len(scanID_list))
                #     current_app.logger.info('=======================================')
                #
                #     order_array = []
                #     for _id in scanID_list:
                #         order_array.append(scan_dict[_id])
                #
                #     current_app.logger.info('==============order_array==============')
                #     current_app.logger.info(len(order_array))
                #     current_app.logger.info('=======================================')
                #
                #     x = col.aggregate([
                #         {
                #             '$match': {
                #                 '_id': {
                #                     '$in': order_array
                #                 }
                #             }
                #         },
                #         {
                #             '$addFields': {
                #                 '_order': {
                #                     '$indexOfArray': [order_array, "$_id"]
                #                 }
                #             }
                #         },
                #         {
                #             '$sort': {
                #                 '_order': 1
                #             }
                #         }
                #     ])

                """ By querying DB directly """
                scan_dict = []
                with open('/simpleFlaskApp/final_scan_dic.tsv', 'r') as tsv:
                    t = csv.reader(tsv)
                    for line in t:
                        if line[0].split('\t')[0] == 'image_id':
                            pass
                        else:
                            scan_dict.append(line[0].split('\t')[1])
                current_app.logger.info(len(scan_dict))

                doc_list = []
                for i in range(10):
                    scan_ID = []
                    for it in result_list[i*(len(result_list)//10):(i+1)*(len(result_list)//10)]:
                        scan_ID.append(it['scanIndex'])
                    current_app.logger.info('=======================================')
                    current_app.logger.info(len(scan_ID))
                    current_app.logger.info('=======================================')

                    order_array = []
                    for zzz in scan_ID:
                        order_array.append(scan_dict[zzz])

                    current_app.logger.info('=======================================')
                    current_app.logger.info(len(order_array))
                    current_app.logger.info('=======================================')

                    x = col.aggregate([
                        {
                            '$match': {
                                '_id': {
                                    '$in': order_array
                                }
                            }
                        },
                        {
                            '$addFields': {
                                '_order': {
                                    '$indexOfArray': [order_array, "$_id"]
                                }
                            }
                        },
                        {
                            '$sort': {
                                '_order': 1
                            }
                        }
                    ])

                    for doc in x:
                        doc_list.append(doc)

                current_app.logger.info('=======================================')
                current_app.logger.info(len(doc_list))
                returnList = jsonify(doc_list)
                return returnList


            if item['checked'] == True:
                high_priority.append(cur_cond)

            elif item['checked'] == False:
                low_priority.append(cur_cond)

        current_app.logger.info('Before OR and query is:')
        # current_app.logger.info(query)
        # x = col.find({'$or': query})

        # x = col.aggregate([
        #     {
        #         '$match': {
        #             '$or': query
        #             }
        #     },
        #     {
        #         '$group': {
        #             '_id': 'null',
        #             'count': {
        #                  '$sum': 1
        #              }
        #         }
        #     }
        # ])
        # for n in x:
        #     total_number_docs = n['count']
        # current_app.logger.info(total_number_docs)
        # if total_number_docs < 30000:
        #     for query_dict in query:
        #         if 'object' in query_dict.keys():
        #             query_dict['object']['$elemMatch']['score']['$gte'] = 0.9
        #
        #
        # x = col.aggregate([
        #     {
        #         '$match': {
        #             '$or': query
        #             }
        #     },
        #     {
        #         '$group': {
        #             '_id': 'null',
        #             'count': {
        #                  '$sum': 1
        #              }
        #         }
        #     }
        # ])
        # for n in x:
        #     total_number_docs = n['count']
        # current_app.logger.info(total_number_docs)
        # if total_number_docs < 30000:
        #     for query_dict in query:
        #         if 'object' in query_dict.keys():
        #             query_dict['object']['$elemMatch']['score']['$gte'] = 0.8
        #
        #
        # x = col.aggregate([
        #     {
        #         '$match': {
        #             '$or': query
        #             }
        #     },
        #     {
        #         '$group': {
        #             '_id': 'null',
        #             'count': {
        #                  '$sum': 1
        #              }
        #         }
        #     }
        # ])
        # for n in x:
        #     total_number_docs = n['count']
        # current_app.logger.info(total_number_docs)
        # if total_number_docs < 30000:
        #     for query_dict in query:
        #         if 'object' in query_dict.keys():
        #             query_dict['object']['$elemMatch']['score']['$gte'] = 0.7
        #
        #
        # x = col.aggregate([
        #     {
        #         '$match': {
        #             '$or': query
        #             }
        #     },
        #     {
        #         '$group': {
        #             '_id': 'null',
        #             'count': {
        #                  '$sum': 1
        #              }
        #         }
        #     }
        # ])
        # for n in x:
        #     total_number_docs = n['count']
        # current_app.logger.info(total_number_docs)
        # if total_number_docs < 30000:
        #     for query_dict in query:
        #         if 'object' in query_dict.keys():
        #             query_dict['object']['$elemMatch']['score']['$gte'] = 0.6
        #
        #
        # x = col.aggregate([
        #     {
        #         '$match': {
        #             '$or': query
        #             }
        #     },
        #     {
        #         '$group': {
        #             '_id': 'null',
        #             'count': {
        #                  '$sum': 1
        #              }
        #         }
        #     }
        # ])
        # for n in x:
        #     total_number_docs = n['count']
        # current_app.logger.info(total_number_docs)
        #
        # if total_number_docs < 30000:
        #     for query_dict in query:
        #         if 'object' in query_dict.keys():
        #             query_dict['object']['$elemMatch']['score']['$gte'] = 0.5
        current_app.logger.info('ttttttttttt')
        current_app.logger.info(query)

        x = col.aggregate([
            {
                '$match': {
                    '$and': query
                    }
            }
        ])

        start = time.time()
        # current_app.logger.info(doc_list)

        doc_list = []
        for doc in x:
            doc_list.append(doc)

        end = time.time()
        current_app.logger.info('doc_list.append(doc)')
        current_app.logger.info(end-start)
        start = time.time()
        if item['type'] == 'object':

            for i in range(len(high_priority)):
                high_priority_object.append(high_priority[i]['object']['$elemMatch']['label'])

            for i in range(len(low_priority)):
                low_priority_object.append(low_priority[i]['object']['$elemMatch']['label'])
            end = time.time()
            scoring_list = [0] * len(doc_list)
            current_app.logger.info('High/Low priority objects divided')
            current_app.logger.info(end-start)
            start = time.time()
            for idx in range(len(doc_list)):
                object_dict_list = doc_list[idx]['object']
                high_score = [0] * len(high_priority_object)
                low_score = [0] * len(low_priority_object)

                for q, high_obj in enumerate(high_priority_object):
                    high_score[q] = [0]

                    for _idx in range(len(object_dict_list)):
                        each_object = object_dict_list[_idx]

                        if each_object['label'] == high_obj:
                            high_score[q].append(each_object['score'])
                        else:
                            pass

                    high_score[q] = max(high_score[q])
                    if high_obj == 'person':
                        high_socre[q] = high_score[q] - 0.5
                ### Isn't 1.0 too large ?
                high_score = list(np.array(high_score) + 1.0)
                ### Isn't 1.0 too large ?

                for q, low_obj in enumerate(low_priority_object):
                    low_score[q] = [0]

                    for _idx in range(len(object_dict_list)):
                        each_object = object_dict_list[_idx]

                        if each_object['label'] == low_obj:
                            low_score[q].append(each_object['score'])
                        else:
                            pass

                    low_score[q] = max(low_score[q])

                scoring_list[idx] = sum(high_score + low_score)
            end = time.time()
            current_app.logger.info("Scoring list made")
            current_app.logger.info(end-start)
            start = time.time()
            for i, score in enumerate(scoring_list):
                doc_list[i]['Sorting_Score'] = score
           
            doc_list = sorted(doc_list, key=lambda x: x['Sorting_Score'], reverse=True)

            end = time.time()
            current_app.logger.info("Sorted!!!")
            current_app.logger.info(end-start)
            current_app.logger.info("Doc list length is %d" %(len(doc_list)))
            current_app.logger.info('Inside high_priority')
            current_app.logger.info(high_priority_object)
            current_app.logger.info('Inside low_priority')
            current_app.logger.info(low_priority_object)
            current_app.logger.info('Finish ordering')


        current_app.logger.info("?????")
        current_app.logger.info(st_query)
        current_app.logger.info(len(st_query))
        if len(st_query) > 0:
            st_x = col.aggregate([
                {
                    '$match': {
                        '$and': st_query
                    }
                }
            ])

            st_doc_list = []
            for doc in st_x:
                st_doc_list.append(doc)

            current_app.logger.info(len(st_doc_list))

            doc_list = st_doc_list + doc_list


        current_app.logger.info('Return results to React')

        start = time.time()
        returnList = jsonify(doc_list)
        end = time.time()
        current_app.logger.info("jsonify")
        current_app.logger.info(end-start)
        current_app.logger.info(len(doc_list))

        # current_app.logger.info('TEST')
        # res = send_test('http://demo2.itec.aau.at:80/vbs/submit', 'VBS_TEST')
        # current_app.logger.info('CHECK')
        # current_app.logger.info(res.text)
        # current_app.logger.info(res.status_code)

        return returnList

# @cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
# @ns.route("/getResult")
# class sendResult(Resource):
#   def post(self):
#     current_app.logger.info('Getting Results')
#     data = request.json
#     data_list = data['myData']
#     current_app.logger.info('Data List')
#     current_app.logger.info(data_list)
#
#     category_list = []
#     sort_type_list = []
#     for data in data_list:
#       type = data['type']
#       if type == 'object':
#         _type = 'localizedObject'
#         _category = 'Text'
#       elif type == 'text':
#         _type = 'OCR'
#       elif type == 'sentence'
#         _type = 'caption'
#       elif type == 'color':
#         _type = 'dominantColor'
#       sort_type_list.append(_type)
#
#
#     result_logging = {"teamID": "IVIST",
#                       "memberID": "2",
#                       "timestamp": int(time.time()),
#                       "usedCategories": ,
#                       "sortType": ,
#                       "resultSetAvailability": ,
#                       "type": ,
#                       "results": ,
#                       }
#
#     requests.post("http://VBS_LOGGING_SERVER:4444/getString", data={})


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
