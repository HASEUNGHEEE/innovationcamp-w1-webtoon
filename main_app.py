from flask import Flask, render_template, request, jsonify, redirect, url_for
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.wvkfw4y.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client.dbwebtoon

import random


@app.route('/')
def main():
    return render_template('main.html')



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

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
