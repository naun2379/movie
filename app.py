from flask import Flask, request, render_template, redirect, url_for, abort, session
import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from urllib.request import urlopen

app = Flask(__name__)

app.secret_key = b'aaa!111/'

@app.route('/movie/<int:num>')
def movie_page(num):
    url = urlopen("https://movie.naver.com/movie/bi/mi/basic.nhn?code=%s" % num)
    bs = BeautifulSoup(url, 'html.parser')
    body = bs.body

    data = []

    # 영화 포스터
    try:
        img = body.find_all(class_="poster")[1].find("a").find("img").get("src")
        data.append(img)
    except IndexError:
        data.append('') 

    target = body.find(class_="wide_info_area")

    # 영화 제목
    title = target.find(class_="h_movie").find("a").text
    data.append(title)

    # 영화 서브 타이틀
    sub_title = target.find(class_="h_movie2").text
    data.append(sub_title)

    # 장르
    try:
        for i in range(0, 5):
            if i == 2:
                infoSub = target.find(class_="info_spec").find_all("span")[i].text
                data.append(infoSub)
            else:
                infoSub = target.find(class_="info_spec").find_all("span")[i].find_all("a")
                infoSubList = [infoSub.text.strip() for infoSub in infoSub]
                data.append(infoSubList)
    except IndexError:
        return render_template('movie.html', data="except_IndexError");

    # 감독
    try:
        director = target.find(class_="info_spec2").find_all("dd")[0].find_all("a")
        directorList = [director.text.strip() for director in director]
        data.append(directorList) 
    except IndexError:
        data.append(['NULL']) 

    # 출연 배우
    try:
        cast = target.find(class_="info_spec2").find_all("dd")[1].find_all("a")
        castList = [cast.text.strip() for cast in cast]
        data.append(castList) 
    except IndexError:
        data.append(['NULL'])

    url = urlopen("https://movie.naver.com/movie/point/af/list.nhn?st=mcode&sword=%s&target=after" % num)
    bs = BeautifulSoup(url, 'html.parser')
    body = bs.body

    naver_data = []

    # 영화 반응 (네이버)
    try:
        for review in body.find_all('td','title'):
            naver_data.append(review.get_text().split('\n')[5])
    except IndexError:
        naver_data.append('NULL')

    url = urlopen("https://suggest-bar.daum.net/suggest?id=movie&cate=movie&q=%s" % quote(title))
    body = url.read().decode("utf-8")

    daum_num_start = body.find("%s|" % title) + (len(title) + 1)
    daum_num_end = daum_num_start + body[daum_num_start:].find("|")
    daum_num = body[daum_num_start:daum_num_end]

    json_data = requests.get("https://search.daum.net/qsearch?mk=0&uk=0&q=%s.json&viewtype=json&w=movie&m=comment" % daum_num).json()

    daum_data = []

    # 영화 반응 (다음)
    try:
        for review in json_data['RESULT']['MOVIE_COMMENT']['comments']:
            daum_data.append(review['comment'])
    except IndexError:
        daum_data.append('NULL')

    return render_template('movie.html', data=data, naver_data=naver_data, daum_data=daum_data)


@app.route('/')
def main():
    # 네이버 영화 크롤링
    url = urlopen("https://movie.naver.com/movie/running/current.nhn")
    bs = BeautifulSoup(url, 'html.parser')
    body = bs.body

    target = body.find(class_="lst_detail_t1")
    list = target.find_all('li')
    no = -1

    datas = []

    for n in range(0, len(list)) :
        no += 1
        datas.append([])

        # 순위
        datas[no].append(no + 1)

        # 영화 제목
        title = list[n].find(class_="tit").find("a").text
        datas[no].append(title) 

        # 영화 번호
        num = list[n].find(class_="thumb").find("a").get("href")
        datas[no].append(num[num.find("?code=")+6:])

        # 영화 포스터
        try:
            img = list[n].find(class_="thumb").find("a").find("img").get("src")
            datas[no].append(img)
        except IndexError:
            datas[no].append('') 

        # 장르
        try:
            genre = list[n].find(class_="info_txt1").find_all("dd")[0].find("span").find_all("a")
            genreList = [genre.text.strip() for genre in genre]
            datas[no].append(genreList) 
        except IndexError:
            datas[no].append(['NULL'])

        # 감독
        try:
            director = list[n].find(class_="info_txt1").find_all("dd")[1].find("span").find_all("a")
            directorList = [director.text.strip() for director in director]
            datas[no].append(directorList) 
        except IndexError:
            datas[no].append(['NULL'])

        # 출연 배우
        try:
            cast = list[n].find(class_="lst_dsc").find("dl", class_="info_txt1").find_all("dd")[2].find(class_="link_txt").find_all("a")
            castList = [cast.text.strip() for cast in cast]
            datas[no].append(castList) 
        except IndexError:
            datas[no].append(['NULL'])
    return render_template('main.html', datas=datas)

if __name__ == '__main__':
    app.run(debug=True)
