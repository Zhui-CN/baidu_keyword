# -*- coding: utf-8 -*-

import time
from flask import Flask, jsonify, request
from utils.client import scrapyd_client, mongodb_client
from uuid import uuid1
from utils.settings import SPIDER_SCRAPYD_NAME, SERVER_IP, SERVER_PORT

app = Flask(__name__)

tips = {
    "check_row": "",
    "pros": [],
    "keyword_list": [
        {
            "keywords": ["知乎"],
            "domain": "www.zhihu.com"
        }
    ]
}


def get_template():
    json_template = {
        "code": 0,
        "msg": "",
        "data": {}
    }
    return json_template


def get_result(job_id):
    json_html = get_template()
    scrapyd = scrapyd_client.get_scrapyd()
    while True:
        time.sleep(1)
        result = scrapyd.job_status(SPIDER_SCRAPYD_NAME, job_id)
        if result:
            if result == "finished":
                json_html['data'] = mongodb_client.find_all(job_id)
                return json_html
        else:
            json_html['code'] = 1
            json_html['msg'] = "job_id不正确，请检查确认"
            return json_html


@app.route('/')
def index():
    json_html = get_template()
    json_html['msg'] = "使用POST方法开启爬虫，参照各式如下，路径：/start"
    json_html['data'] = tips
    return jsonify(json_html)


@app.route('/start', methods=['GET', 'POST'])
def spider_start():
    json_html = get_template()
    if request.method == "POST":
        body_data = request.form
        json_data = request.data
        if not body_data and not json_data:
            json_html['code'] = 1
            json_html['msg'] = "请求体不正确"
            return jsonify(json_html)

        settings = body_data if body_data else eval(json_data)

        settings_dict = {}
        for key, value in settings.items():
            settings_dict[key.upper()] = eval(value) if isinstance(value, str) and value != "" else value

        if not settings_dict.get("KEYWORD_LIST"):
            json_html['code'] = 1
            json_html['msg'] = "keyword_list参数错误"
            return jsonify(json_html)

        scrapyd = scrapyd_client.get_scrapyd()
        job_uuid = str(uuid1()).replace('-', '')
        settings_dict["JOB_ID"] = job_uuid
        scrapyd.schedule(SPIDER_SCRAPYD_NAME, "baidu", settings=settings_dict, jobid=job_uuid)

        json_html['code'] = 0
        json_html['msg'] = "提交成功"
        json_html['data'] = "任务id为：{} 查询地址：{}:{}/result?job_id={}".format(job_uuid, SERVER_IP, SERVER_PORT, job_uuid)
        return jsonify(json_html)

    json_html['code'] = 1
    json_html['msg'] = "当前GET请求，要运行爬虫则使用POST，参照各式如下"
    json_html['data'] = tips
    return jsonify(json_html)


@app.route('/result')
def search_result():
    json_html = get_template()
    job_id = request.args.get('job_id')

    if not job_id:
        json_html['code'] = 1
        json_html['msg'] = "缺少job_id"
        return jsonify(json_html)

    json_html = get_result(job_id)
    return jsonify(json_html)


if __name__ == '__main__':
    app.run(host=SERVER_IP, port=SERVER_PORT)
