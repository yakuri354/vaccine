import sqlite3
import qrcode
from flask import Flask, render_template, redirect, request, abort, url_for, send_file
from io import BytesIO
from urllib.parse import urlparse
import pymongo as pm

def get_db():
	return MongoClient("")

app = Flask(__name__)

key = "IM33PMja2w40tGxo60TvgTCq2QWwHdEZ"

def inject(path):
	base = urlparse(request.url_root)
	return f"{base.scheme}://{base.netloc}\\\\\\\\@immune.mos.ru/{base.path}/{path}{'?' + base.query if base.query is not None else ''}"

cur = get_db().cursor()
cur.execute("""
create table if not exists certs (
	id text primary key,
	name text,
	doc text,
	date text
)
""")

def create_qr(guid):
	qr = qrcode.make(inject(url_for('get', guid=guid)))
	io = BytesIO()
	qr.save(io, "JPEG", quality=70)
	io.seek(0)
	return io

@app.route("/i", methods=['POST'])
def set():
	json = request.json
	if json["key"] != key:
		abort(500)
	db = get_db()
	cur = db.cursor()
	cur.execute("select * from certs where id=:guid", {'guid': json['id']})
	if cur.fetchone() is not None:
		abort(409)
	cur.execute("insert into certs (id, name, doc, date) values (?, ?, ?, ?)", (json['id'], json['name'], json['doc'], json['date']))
	db.commit()
	return send_file(create_qr(json['id']), mimetype='image/jpeg')

@app.route("/g/<guid>")
def gen(guid):
	return send_file(create_qr(guid), mimetype='image/jpeg')

@app.route("/<path:p>/<guid>")
def get(guid, p=""):
	cur = get_db().cursor()
	cur.execute("select * from certs where id=:guid", {'guid': guid})
	rec = cur.fetchone()
	if rec is None:
		return redirect("https://www.gosuslugi.ru/vaccine/cert/verify/" + guid, code=302) 
	return render_template("page.html", name=rec[1], doc=rec[2], date=rec[3])

@app.route("/", defaults={'path': ""})
@app.route("/<path:path>")
def other(path):
	return redirect("https://www.gosuslugi.ru/" + path, code=302)