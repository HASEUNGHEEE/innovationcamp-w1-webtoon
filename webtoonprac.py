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
# 그렇지 않으면, 개발자(=나)가 회원들의 비밀번호를 볼 수 있으니까요.^^;
import hashlib

import random
import certifi
ca = certifi.where()
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

#################################
##  HTML을 주는 부분             ##
#################################
@app.route('/')
def main():
    return render_template('main.html')


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    # 로그인한 토큰이 있는 경우(로그인 완료한 류저)
    if token_receive != None:
        try:
            # 토큰으로부터 payload를 불러옴
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            userinfo = db.user.find_one({"user_id": payload['id']})
            # payload 내에 있는 user_id를 변수에 할당
            user_id = userinfo['user_id']
            login_status = 1
            return render_template('index.html', user_id=user_id, login_status =login_status)
        except jwt.ExpiredSignatureError:
            return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
    else:
        login_status = 0
        return render_template('index.html', login_status=login_status)



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


#################################
##  로그인을 위한 API            ##
#################################

# [회원가입 API]
# id, pw, nickname을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/sign_up/save', methods=['POST'])
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

@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    # 회원 아이디 중복 확인
    # 데이터 베이스에서 회원 아이디가 존재하는지 확인하고
    # 중복 유무를 exists 변수에 담아서 반환
    username_receive = request.form['username_give']
    exists = bool(db.t_user.find_one({"user_id": username_receive}))
    # print(value_receive, type_receive, exists)
    return jsonify({'result': 'success', 'exists': exists})

# @app.route('/api/login', methods=['POST'])
# def api_login():
#     id_receive = request.form['id_give']
#     pw_receive = request.form['pw_give']
#
#     # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
#     pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
#
#     # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
#     result = db.user.find_one({'id': id_receive, 'pw': pw_hash})
#
#     # 찾으면 JWT 토큰을 만들어 발급합니다.
#     if result is not None:
#         # JWT 토큰에는, payload와 시크릿키가 필요합니다.
#         # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
#         # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
#         # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
#         payload = {
#             'id': id_receive,
#             'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=5)
#         }
#         token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
#
#         # token을 줍니다.
#         return jsonify({'result': 'success', 'token': token})
#     # 찾지 못하면
#     else:
#         return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})
#
#
# # [유저 정보 확인 API]
# # 로그인된 유저만 call 할 수 있는 API입니다.
# # 유효한 토큰을 줘야 올바른 결과를 얻어갈 수 있습니다.
# # (그렇지 않으면 남의 장바구니라든가, 정보를 누구나 볼 수 있겠죠?)
# @app.route('/api/nick', methods=['GET'])
# def api_valid():
#     token_receive = request.cookies.get('mytoken')
#
#     # try / catch 문?
#     # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.
#
#     try:
#         # token을 시크릿키로 디코딩합니다.
#         # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         print(payload)
#
#         # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
#         # 여기에선 그 예로 닉네임을 보내주겠습니다.
#         userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
#         return jsonify({'result': 'success', 'nickname': userinfo['nick']})
#     except jwt.ExpiredSignatureError:
#         # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
#         return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
#     except jwt.exceptions.DecodeError:
#         return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})
#




@app.route('/webtoon', methods=['POST'])
def posting():
    # # name_receive = 토큰의 id 를 이용하여 db 에서 이름 가져오기
    # token_receive = request.cookies.get('mytoken')
    #     try:
    #         # 토큰으로부터 payload를 불러옴
    #         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    #         userinfo = db.user.find_one({"user_id": payload['id']})
    #         # payload 내에 있는 user_id를 변수에 할당
    #         user_id = userinfo['user_id']


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
            desc = detailInfo.select_one('p').text.replace('<br/>', '\n')
            genre = detailInfo.select_one('.genre').text
            writer = detailInfo.select_one('.wrt_nm').text[8:]


            doc = {
                # "user_id": user_info["username"],
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
        # except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        #     return redirect(url_for("home"))


@app.route("/webtoon", methods=['GET'])
def listing():
    webtoon_list = list(db.t_webtoon.find({}, {'_id': False}))
    random_list = random.sample(webtoon_list, k=4)

    return jsonify({'webtoons': random_list})
    # token_receive = request.cookies.get('mytoken')
    # try:
    #     payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    #     # 포스팅 목록 받아오기
    #     return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다."})
    # except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
    #     return redirect(url_for("home"))




# 더미 글읽기페이지
# detail 페이지 response가 이걸로 들어감..주의!!
# @app.route('/detail')
# def detail():
#     return render_template('detail.html')

# 뷰어화면 웹툰별 데이터 가져오기
@app.route("/detail/<keyword>")
def info_get(keyword):
    target_webtoon = db.t_webtoon.find_one({'name': keyword}, {'_id': False})
    result = target_webtoon
    return render_template("detail.html", title=keyword, result=result)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)