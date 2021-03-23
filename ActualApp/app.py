import os
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)
from flask_pymongo import PyMongo
from pymongo import MongoClient
import json
from bson import json_util
import numpy
import pickle
import pandas as pd

app = Flask(__name__)


#connect to MongoDB Atlas database
client= MongoClient("mongodb://dbUser:dbUser@cluster0-shard-00-00.lfpww.mongodb.net:27017,cluster0-shard-00-01.lfpww.mongodb.net:27017,cluster0-shard-00-02.lfpww.mongodb.net:27017/<dbname>?ssl=true&replicaSet=atlas-za5qq0-shard-0&authSource=admin&retryWrites=true&w=majority")
db = client.covid_db
collection_symptoms_answer=db["symptoms_anwser"]

@app.route('/')
def symptomPage():
    return render_template("index.html")

@app.route('/GDP')
def GDPPage():
    return render_template("GDP.html")

# #service route
# #covid GDP data route
@app.route("/api_covid_GDP")
def GDPRoute():
    test=db.get_collection("collection_covid_GDP").find()
    master_list=[]
    for i in test:
        master_list.append(i)
    for i in master_list:
        del i['_id']

    return jsonify(master_list)

#symptom data route
@app.route("/symptom.html",methods=['GET','POST'])
def covid_form():
    if request.method == 'POST':
        cough=request.form['cough']
        fever=request.form['fever']
        sore_throat=request.form['sore_throat']
        shortness_of_breath=request.form['shortness_of_breath']
        head_ache=request.form['head_ache']
        age_60_and_above=request.form['age_60_and_above']
        gender=request.form['gender']
        test_indication=request.form['test_indication']

        data={"cough":cough,
        "fever":fever,
        "sore_throat":sore_throat,
        "shortness_of_breath":shortness_of_breath,
        "head_ache":head_ache,
        "age_60_and_above":age_60_and_above,
        "gender":gender,
        "test_indication":test_indication
        }
        db.collection_symptoms_answer.insert_one(data).inserted_id
        return render_template("index.html")
    return render_template("index.html")

@app.route("/answer")
def symptomRoute():
    test=db.get_collection("collection_symptoms_answer").find({}).limit(1).sort("_id",-1)
    master_list=[]
    for i in test:
        master_list.append(i)
    for i in master_list:
        del i['_id']

    dataframe= pd.DataFrame.from_dict(master_list)
    filename='SVC_model.sav'
    loaded_model = pickle.load(open(filename,'rb'))
    y_predict = loaded_model.predict(dataframe)
    return y_predict[0]


if __name__ == "__main__":
    app.run(debug=True)