import jwt
# import hashlib
# from werkzeug.utils import secure_filename

from flask import Flask, render_template, jsonify, request, redirect, url_for
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.wvkfw4y.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client.dbwebtoon

## HTML을 주는 부분
@app.route('/')
def home():
    return render_template('main.html')
        # token_receive = request.cookies.get('mytoken')
        # try:
        #     payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        #
        # except jwt.ExpiredSignatureError:
        #     return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
        # except jwt.exceptions.DecodeError:
        #     return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))



@app.route('/webtoon', methods=['POST'])
def posting():
    # token_receive = request.cookies.get('mytoken')
    # try:
    #     payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    #     user_info = db.users.find_one({"username": payload["id"]})
        url_receive = request.form['url_give']
        star_receive = request.form['star_give']
        comment_receive = request.form["comment_give"]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        data = requests.get(url_receive, headers=headers)

        soup = BeautifulSoup(data.text, 'html.parser')
        image = soup.select_one('meta[property="og:image"]')['content']

        doc = {
            # "user_id": user_info["username"],
            "webtoon_image": image,
            "webtoon_url": url_receive,
            "comment": comment_receive,
            "comment_star": star_receive
        }
        db.t_comment.insert_one(doc)

        return jsonify({"result": "success", 'msg': '포스팅 성공'})
    # except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
    #     return redirect(url_for("home"))


@app.route("/webtoon", methods=['GET'])
def listing():
    webtoon_list = list(db.t_comment.find({}, {'_id': False}))
    return jsonify({'webtoons': webtoon_list})
    # token_receive = request.cookies.get('mytoken')
    # try:
    #     payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    #     # 포스팅 목록 받아오기
    #     return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다."})
    # except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
    #     return redirect(url_for("home"))

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)
