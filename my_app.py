from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.clgy5.mongodb.net/cluster0?retryWrites=true&w=majority')
db = client.dbwebtoon


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/mypage')
def detail():
    username = "username1"
    return render_template('mypage.html', name=username)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)



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
        name = soup.select_one('meta[property="og:title"]')['content']
        desc = soup.select_one('meta[property="og:description"]')['content']

        doc = {
            "url": url_receive,
            "star": star_receive,
            "comment": comment_receive,
        }
        db.t_webtoon.insert_one(doc)

        return jsonify({"result": "success", 'msg': '포스팅 완료'})
    # except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
    #     return redirect(url_for("home"))

@app.route("/webtoon", methods=['GET'])
def listing():
    webtoon_list = list(db.dbwebtoon.find({}, {'_id': False}))
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

# @app.route("/dbwebtoon", methods=["GET"])
# def dbwebtoon_get():
#     dbwebtoon_list = list(db.dbwebtoon.find({}, {'_id': False}))
#     return jsonify({'dbwebtoon': dbwebtoon_list})

