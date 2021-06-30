import sqlite3
import qrcode
from flask import Flask, render_template, redirect, request, abort, url_for, send_file
from io import BytesIO

DATABASE = "app.db"

app = Flask(__name__)

key = "IM33PMja2w40tGxo60TvgTCq2QWwHdEZ"

cur = sqlite3.connect(DATABASE).cursor()
cur.execute("""
create table if not exists certs (
	id text primary key,
	name text,
	doc text,
	date text
)
""")

def get_db():
	return sqlite3.connect(DATABASE)

def create_qr(guid):
	qr = qrcode.make(request.url_root[:-1] + url_for('get', guid=guid))
	io = BytesIO()
	qr.save(io, "JPEG", quality=70)
	io.seek(0)
	return io

@app.route("/v/<guid>")
def get(guid):
	cur = get_db().cursor()
	cur.execute("select * from certs where id=:guid", {'guid': guid})
	rec = cur.fetchone()
	if rec is None:
		return redirect("https://www.gosuslugi.ru/vaccine/cert/verify/" + guid, code=302) 
	return render_template("page.html", name=rec[1], doc=rec[2], date=rec[3])

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

@app.route("/", defaults={'path': ""})
@app.route("/<any:path>")
def other(path):
	return redirect("https://www.gosuslugi.ru/" + path, code=302)