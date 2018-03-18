import json, io
from uwsgidecorators import postfork
from cassandra.cluster import Cluster
from flask import Flask, jsonify, request, send_file

@postfork
def connect():
    global session
    session = Cluster().connect('hw4')


app = Flask(__name__)


@app.route("/deposit", methods=['POST'])
def deposit():
    filename = request.form['filename']
    contents = request.files['contents']
 
    contents_data = contents.read()
    contents_blob = bytearray(contents_data)

    session.execute(
	"""
	INSERT INTO imgs (filename, contents)
	VALUES(%s, %s)
	""",
	(filename, contents_blob)
    )

    return jsonify({ 'status': 'OK' })


@app.route("/retrieve", methods=['GET'])
def retrieve():
    try:
	filename = request.args.get('filename', type=str)
    	row = session.execute(
		"""
		SELECT contents FROM imgs
		WHERE filename = %s
		""",
		[filename]
    	)
    
    	image = io.BytesIO(row[0][0])
    	mimetype = str('image/' + filename.split('.')[1])
        
	return send_file(image, attachment_filename=filename, mimetype=mimetype) 
    except Exception:
	return jsonify({ 'status': 'ERROR' })


if __name__ == "__main__":
    app.run(host='0.0.0.0')
