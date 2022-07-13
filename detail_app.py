from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.xynlbr0.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbwebtoon

# 메인페이지(임의)
@app.route('/')
def main():
    return render_template('main.html')

# 뷰어화면 웹툰별 데이터 가져오기
@app.route("/detail/<keyword>")
def info_get(keyword):
    result = db.t_webtoon.find_one({'name': keyword}, {'_id': False})
    results = list(db.t_webtoon.find({'name': keyword}, {'_id':False}))
    return render_template("detail.html", title=keyword, result=result, results=results)

# doc = {
#     "name": "독립일기",
#     "genre": "에피소드, 일상",
#     "writer": "자까",
#     "desc": "처음으로 나만의 집이 생긴다면? <br>자까 작가의 나혼자 사는 이야기",
#     "image": "https://shared-comic.pstatic.net/thumb/webtoon/748105/thumbnail/thumbnail_IMAG19_d8bd40f2-76f6-448b-8650-126c0d5137b6.jpg",
#     "url": "https://comic.naver.com/webtoon/list?titleId=748105&weekday=thu",
#     "comment": "가나다라마바사 아자차카타파하",
#     "user_id": "testing",
#     "star": "4",
# }
# db.t_webtoon.insert_one(doc)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)