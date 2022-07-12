from flask import Flask, render_template, request, jsonify
app = Flask(__name__)
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient(
    'mongodb+srv://bravadosw:tnsdnr~1951@cluster0.txwl0.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbwebtoon


@app.route('/')
def main():
    return render_template("main.html")


@app.route('/mypage')
def detail():
    return render_template("mypage.html")


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/dbwebtoon", methods=["POST"])
def dbwebtoon_post():
    url_receive = request.form['url_give']
    star_receive = request.form['star_give']
    comment_receive = request.form['comment_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    title = soup.select_one('meta[property="og:title"]')['content']
    image = soup.select_one('meta[property="og:image"]')['content']
    desc = soup.select_one('meta[property="og:description"]')['content']

    doc = {
        'title': title,
        'image': image,
        'desc': desc,
        'star': star_receive,
        'comment': comment_receive,

        # 'user_id' : user_id,
        # 'user_pw' :  user_pw,
        # 'user_email' : user_email,
        # 'webtoon_url' : webtoon_url,
        # 'user_id' : user_id,
        # 'webtoon_url' :webtoon_url,
        # 'comment' : comment,
        # 'comment_star': comment_star
    }
    db.dbwebtoon.insert_one(doc)

    return jsonify({'msg': '저장 완료!'})


@app.route("/dbwebtoon", methods=["GET"])
def dbwebtoon_get():
    dbwebtoon_list = list(db.dbwebtoon.find({}, {'_id': False}))
    return jsonify({'dbwebtoon': dbwebtoon_list})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
