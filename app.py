from flask import Flask, request, jsonify, render_template, redirect 
from flask import make_response
from flask_cors import CORS, cross_origin
from flask_cors import CORS
import shutil
import json
import uuid
from datetime import datetime
import os
import base64
from main import VisaExtract
import shutil

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
path_ = 'C:/air_ticket/visa_extraction/'

def document(data, field_type: str, document_type: str, user_name='Anonymous', filters=None, version=False, meta_info=None):

    date = str(datetime.now().timestamp()).replace(".", "")
    staticFileName = os.path.join(path_, f"static/uploads/documents/{date}.pdf")
    # staticFileName = f"static/uploads/documents/{date}.pdf"
    filename = os.path.join(path_, f"documents/{date}.pdf")
    with open(os.path.join(path_, f"documents/{date}.pdf"), "wb") as fp:
        fp.write(base64.decodebytes(data.encode()))
        shutil.copyfile(os.path.join(path_, f'documents/{date}.pdf'), staticFileName)
    if " " in field_type:
        field_type = field_type.lower().replace(" ", "_")
    img_obj = VisaExtract(filename, document_type, field_type, "document")
    if field_type == "all":
        print("hey")
        # json_data = {f"{field_type}": img_obj.get_output()}
        json_data = img_obj.get_output()
        print(json_data)
    else:
        json_data = [{f"{field_type}": img_obj.get_output()}]
    # return jsonify(json_data)
    resp = make_response(jsonify(json_data))
    # resp = make_response(jsonify({"all": json_data, "document_type": document_type}), 200)
    resp.headers.add("Access-Control-Allow-Origin", "*")
    return resp


    # final = {}
    # final['file_id'] = str(uuid.uuid1())
    # final['data'] = json_data
    # final['document_type'] = document_type
    # final['file_type'] = 'document'
    # i = staticFileName.index("static")
    # final['file_path'] = staticFileName[i:]
    
    # # final['filter_type'] = filters
    # # final['language_type'] = lang
    # # return render_template("info.html", final1=final)
    
    # resp = make_response(jsonify({"all": json_data, "document_type": document_type}), 200)
    # if meta_info:
    #     resp = make_response(jsonify({"all": json_data, "document_type": document_type, "meta_info": meta_info}))
    # resp.headers.add("Access-Control-Allow-Origin", "*")
    # return resp


# url for api
@app.route("/get_info", methods=['GET', 'POST'])
@cross_origin()
def api_call():

    if request.method == 'POST':
        values = eval(request.data.decode())
        meta_info = request.args
        if values.get('image'):
            data = values.get('image')
        else:
            data = values.get('pdf')
        document_type = values['document_type']
        field_type = values['field_type']
        file_type = values['file_type']
        if file_type.lower() == "document":
            output = document(data, field_type, document_type, version='2', meta_info=meta_info) 
#               output['document_type'] = document_type
            print("OUTPUT --> ", output)
            return output
        else:
            return "Incorrect file type", 404 

    # except Exception as err:
        # print("\n Error --> ", err)
        # return '',404

if __name__ == '__main__':
    app.run(debug=True)