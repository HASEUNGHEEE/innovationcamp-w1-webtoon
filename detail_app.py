from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.xynlbr0.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbwebtoon

# 메인페이지
@app.route('/')
def main():
    return render_template('main.html')

# 파라미터
# @app.route('/detail/<title>')
# def detail(title):
#     return render_template('detail.html', title=title)

# 더미 글읽기페이지
# detail 페이지 response가 이걸로 들어감..주의!!
# @app.route('/detail_page')
# def detail():
#     return render_template('detail.html')

# 글 읽기 화면 웹툰별로 t_webtoon 데이터 가져오기
@app.route("/detail/<keyword>")
def info_get(keyword):
    target_webtoon = db.t_webtoon.find_one({'name': keyword}, {'_id': False})
    result = target_webtoon
    return render_template("detail.html", title=keyword, result=result)


# 해당 웹툰 코멘트
@app.route("/detail/<keyword>")
def comment_get(keyword):
    key = request.form.get['name']
    comment_lists = db.t_webtoon.find_one({'name': key}, {'_id': False})
    return jsonify({'comment_list': comment_lists})



# doc = {
#     "name": "독립일기",
#     "genre": "에피소드, 일상",
#     "writer": "자까",
#     "desc": "'이건 내가 아는 그 전개다' 한순간에 세계가 멸망하고, 새로운 세상이 펼쳐졌다. 오직 나만이 완주했던 소설 세계에서 평범했던 독자의 새로운 삶이 시작된다.",
#     "image": "https://shared-comic.pstatic.net/thumb/webtoon/748105/thumbnail/thumbnail_IMAG06_fa3bf10d-1b8f-40cd-a8eb-01caf9bbc3e4.jpg",
#     "url": "https://comic.naver.com/webtoon/list?titleId=748105&weekday=thu",
#     "comment": "재밌어용",
#     "user_id": "innovationcamp",
#     "star": "5",
# }
# db.t_webtoon.insert_one(doc)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)