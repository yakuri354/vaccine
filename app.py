import sqlite3
import qrcode
from flask import Flask, render_template, redirect, request, abort, url_for, send_file
from io import BytesIO
from urllib.parse import urlparse, urlencode
app = Flask(__name__)

def inject(name, doc, date):
	base = urlparse(request.url_root)
	return f"{base.scheme}://{base.netloc}\\\\\\\\@www.gosuslugi.ru/vaccine/cert/verify/https://www.gosuslugi.ru/vaccine/cert/verify/d" + urlencode({"name": name, "doc": doc, "date": date})
	#return f"{base.scheme}://{base.netloc}\\\\\\\\@immune.mos.ru/d?" + urlencode({"name": name, "doc": doc, "date": date})

def create_qr(name, doc, date):
	qr = qrcode.make(inject(name, doc, date))
	io = BytesIO()
	qr.save(io, "JPEG", quality=70)
	io.seek(0)
	return io

@app.route("/g", methods = ['POST'])
def gen():
	return send_file(create_qr(request.json["name"], request.json["doc"], request.json["date"]), mimetype='image/jpeg')

@app.route("/<path:path>/d")
def get(path=""):
	return render_template("page.html", name=request.args.get("name"), doc=request.args.get("doc"), date=request.args.get("date"))

@app.route("/", defaults={'path': ""})
@app.route("/<path:path>")
def other(path):
	return redirect("https://www.gosuslugi.ru/" + path, code=302)