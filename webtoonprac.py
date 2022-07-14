from flask import Flask, render_template, jsonify, request, session, redirect, url_for

app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.wvkfw4y.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client.dbwebtoon

# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = 'SPARTA'

# JWT 패키지를 사용합니다. (설치해야할 패키지 이름: PyJWT)
import jwt

# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용합니다.
import datetime

# 회원가입 시엔, 비밀번호를 암호화하여 DB에 저장해두는 게 좋습니다.
import hashlib

import random
import certifi
ca = certifi.where()
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

# @app.route('/')
# def main():
#     return render_template('main.html')

# 로그인 및 회원가입
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userinfo = db.t_user.find_one({"user_id": payload["id"]})
        user_id = userinfo['user_id']
        # print(user_id)
        return render_template('main.html', user_id=user_id)
    except jwt.ExpiredSignatureError:
        return render_template('main.html')
    except jwt.exceptions.DecodeError:
        return render_template('main.html')

@app.route('/register')
def register_back():
    msg = request.args.get("msg")
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userinfo = db.t_user.find_one({"user_id": payload["id"]})
        user_id = userinfo['user_id']
        return render_template('index.html', user_id=user_id, msg="현재 로그인되어 있습니다.")
    except jwt.ExpiredSignatureError:
        return render_template('register.html', msg=msg)
    except jwt.exceptions.DecodeError:
        return render_template('register.html', msg=msg)

@app.route('/update')
def update_back():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userinfo = db.t_user.find_one({"user_id": payload["id"]})
        user_id = userinfo['user_id']
        return render_template('update.html', user_id=user_id, msg="현재 로그인되어 있습니다.")
    except jwt.ExpiredSignatureError:
        return render_template('login.html', msg="로그인 정보가 존재하지 않습니다.")
    except jwt.exceptions.DecodeError:
        return render_template('login.html', msg="로그인 정보가 존재하지 않습니다.")

@app.route('/update/save', methods=['POST'])
def update():
    email_receive = request.form['email_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "user_email": email_receive,
        "user_pw": password_hash,
    }
    db.t_user.update_one(doc)
    return jsonify({'result': 'success'})


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인을 시도하는 사용자의 아이디
    username_receive = request.form['username_give']
    # 로그인을 시도하는 사용자의 패스워드
    password_receive = request.form['password_give']
    # 해쉬를 이용하여 사용자 비밀번호 암호화
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # 암호화한 비밀번호를 database에 저장
    result = db.t_user.find_one({'user_id': username_receive, 'user_pw': pw_hash})

    # 회원정보가 db에 존재할 경우 토큰생성
    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        return jsonify({'result': 'success', 'token': token})
    # 존재하지 않을 경우
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# [회원가입 API]
# id, pw, nickname을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/register/save', methods=['POST'])
def sign_up():
    # 회원 가입을 시도하는 사용자의 아이디
    username_receive = request.form['username_give']
    # 회원 가입을 시도하는 사용자의 이메일
    email_receive = request.form['email_give']
    # 회원 가입을 시도하는 사용자의 패스워드
    password_receive = request.form['password_give']
    # 사용자 패스워드 암호화
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "user_id": username_receive,
        "user_email": email_receive,
        "user_pw": password_hash,
    }
    # 데이터 베이스에 회원 정보 저장
    db.t_user.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/register/check_dup', methods=['POST'])
def check_dup():
    # 회원 아이디 중복 확인
    # 데이터 베이스에서 회원 아이디가 존재하는지 확인하고
    # 중복 유무를 exists 변수에 담아서 반환
    username_receive = request.form['username_give']
    exists = bool(db.t_user.find_one({"user_id": username_receive}))
    # print(value_receive, type_receive, exists)
    return jsonify({'result': 'success', 'exists': exists})


# 메인 글쓰기
@app.route('/webtoon', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    if (token_receive is not None):
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userinfo = db.t_user.find_one({"user_id": payload["id"]})
        user_id = userinfo['user_id']

    url_receive = request.form['url_give']
    star_receive = request.form['star_give']
    comment_receive = request.form["comment_give"]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, "lxml")
    image = soup.select_one('meta[property="og:image"]')['content']
    name = soup.select_one('meta[property="og:title"]')['content']

    detailInfo = soup.select_one('.comicinfo > .detail')
    desc = detailInfo.select_one('p').text
    genre = detailInfo.select_one('.genre').text
    writer = detailInfo.select_one('.wrt_nm').text[8:]

    doc = {
        "user_id": user_id,
        "image": image,
        "url": url_receive,
        "comment": comment_receive,
        "star": star_receive,
        "name": name,
        "desc": desc,
        "genre": genre,
        "writer": writer
    }
    db.t_webtoon.insert_one(doc)

    return jsonify({"result": "success", 'msg': '포스팅 완료'})

# 메인페이지 카드 리스팅
@app.route("/webtoon", methods=['GET'])
def listing():
    webtoon_list = list(db.t_webtoon.find({}, {'_id': False}))
    random_list = random.sample(webtoon_list, k=8)

    return jsonify({'webtoons': random_list})

# # 개별 웹툰 페이지
# @app.route('/detail')
# def detail():
#     try:
#         return render_template('detail.html')
#     except jwt.ExpiredSignatureError:
#         return render_template('detail.html')
#     except jwt.exceptions.DecodeError:
#         return render_template('detail.html')

# 개별 웹툰페이지로 이동
@app.route("/detail/<keyword>")
def info_get(keyword):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userinfo = db.t_user.find_one({"user_id": payload["id"]})
        user_id = userinfo['user_id']
        result = db.t_webtoon.find_one({'name': keyword}, {'_id': False})
        results = list(db.t_webtoon.find({'name': keyword}, {'_id': False}))
        return render_template('detail.html', user_id=user_id,  title=keyword, result=result, results=results)
    except jwt.ExpiredSignatureError:
        result = db.t_webtoon.find_one({'name': keyword}, {'_id': False})
        results = list(db.t_webtoon.find({'name': keyword}, {'_id': False}))
        return render_template('detail.html', title=keyword, result=result, results=results)
    except jwt.exceptions.DecodeError:
        result = db.t_webtoon.find_one({'name': keyword}, {'_id': False})
        results = list(db.t_webtoon.find({'name': keyword}, {'_id': False}))
        return render_template('detail.html', title=keyword, result=result, results=results)

# 마이페이지
# @app.route('/mypage')
# def mypage():
#     token_receive = request.cookies.get('mytoken')
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         userinfo = db.t_user.find_one({"user_id": payload["id"]})
#         user_id = userinfo['user_id']
#         return render_template('mypage.html', user_id=user_id, msg="현재 로그인되어 있습니다.")
#     except jwt.ExpiredSignatureError:
#         return render_template('login.html', msg="로그인 정보가 존재하지 않습니다.")
#     except jwt.exceptions.DecodeError:
#         return render_template('login.html', msg="로그인 정보가 존재하지 않습니다.")

@app.route("/mypage/<user_page_id>")
def asdf(user_page_id):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userinfo = db.t_user.find_one({"user_id": payload["id"]})
        user_id = userinfo['user_id']
        results = list(db.t_webtoon.find({'user_id': user_page_id}, {'_id': False}))
        return render_template('mypage.html', user_id=user_id, user_page_id=user_page_id, results=results)
    except jwt.ExpiredSignatureError:
        results = list(db.t_webtoon.find({'user_id': user_page_id}, {'_id': False}))
        return render_template('mypage.html', user_page_id=user_page_id, results=results)
    except jwt.exceptions.DecodeError:
        results = list(db.t_webtoon.find({'user_id': user_page_id}, {'_id': False}))
        return render_template('mypage.html', user_page_id=user_page_id, results=results)


def masdf(user_id):
    results = list(db.t_webtoon.find({'user_id': user_id}, {'_id': False}))
    return render_template("mypage.html", results=results, user_page_id=user_id)

@app.route('/mypage', methods=['POST'])
def my_posting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_id = payload["id"]

        url_receive = request.form['url_give']
        star_receive = request.form['star_give']
        comment_receive = request.form["comment_give"]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        data = requests.get(url_receive, headers=headers)

        soup = BeautifulSoup(data.text, "lxml")
        image = soup.select_one('meta[property="og:image"]')['content']
        name = soup.select_one('meta[property="og:title"]')['content']
        detailInfo = soup.select_one('.comicinfo > .detail')
        desc = detailInfo.select_one('p').text
        genre = detailInfo.select_one('.genre').text
        writer = detailInfo.select_one('.wrt_nm').text[8:]

        doc = {
            "user_id": user_id,
            "image": image,
            "url": url_receive,
            "comment": comment_receive,
            "star": star_receive,
            "name": name,
            "desc": desc,
            "genre": genre,
            "writer": writer
        }
        db.t_webtoon.insert_one(doc)
        return jsonify({"result": "success", 'msg': '포스팅 완료'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template('index.html')

@app.route("/mypage", methods=['GET'])
def my_listing():
    webtoon_list = list(db.dbwebtoon.find({}, {'_id': False}))
    return jsonify({'webtoons': webtoon_list})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)