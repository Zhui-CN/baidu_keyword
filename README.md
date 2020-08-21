# BaiduKeyWordSpider  And  Server
百度搜索关键词网站域名排名爬虫(包含爬虫与服务端)

### Install

```
git clone https://github.com/Zhui-CN/baidu_keyword.git
cd baidu_keyword
pip install -r requirements.txt
```

### BaiDuSearchSpider

百度搜索关键词域名排名爬虫

```python
Run:
    scrapy crawl baidu
    
BaiDuSearchSpider/BaiDu/settings.py
MONGODB_XXX		mongodb配置参数
CHECK_ROW		查询一页个数，默认10个
KEYWORD_LIST = [
    {
        "keywords": ["知乎"],
        "domain": "www.zhihu.com"
    },
    {
        "keywords": ["YSL"],
        "domain": "www.yslbeautycn.com"
    }
]
PROS = []		代理ip需要的参数，暂不可用，可自行调整

```

### BaiDuSearchFlask

百度搜索关键词域名排名Flask Server

```python
Run:
    cd log  shell: scrapyd
    cd BaiDuSearchFlask  python searchserver.py
    
BaiDuSearchFlask/utils/settings.py
CLIENT_XXX = "XXX"			scrapyd配置参数
MONGODB_XXX = "XXX"			mongodb配置参数
SPIDER_SCRAPYD_NAME = "XXX" spider deploy name
SERVER = "XXX"				server ip and port
```

### Run

1. Edit Configure： 

   ```
   BaiDuSearchFlask/utils/settings.py
   BaiDuSearchSpider/BaiDu/settings.py
   ```

2. push spider deploy

   ```python
   cd log 
   shell: scrapyd
   python push_spider.py
   ```

3. run BaiDuSearchFlask

   ```python
   python searchserver.py
   ```

4. API

   1. url: ip:port/start

      ```python
      GET:
      	index
      POST (json or form-data):
      	example:
              {
                  "check_row": "",
                  "pros": [],
                  "keyword_list": [
                      {
                          "keywords": ["知乎"],
                          "domain": "www.zhihu.com"
                      },
                      {
                          "keywords": ["zhihu"],
                          "domain": "www.zhihu.com"            
                      }
          		]
      		}
      return:
          {
              "code": 0,
              "data": "任务id为：85618a92e37e11ea9a5418c04d1eda18 查询地址：0.0.0.0:9000/result?job_id=85618a92e37e11ea9a5418c04d1eda18",
              "msg": "提交成功"
          }
      ```

   2. url: ip:post/result?job_id=

      ```python
      GET:
          parameter:
              job_id 启动爬虫返回的id
      return:
          {
              "domain" : "www.zhihu.com",
              "ip" : null,
              "keyword" : "知乎",
              "address" : null,
              "check_row" : 10,
              "job_id" : "85618a92e37e11ea9a5418c04d1eda18",
              "page_numb" : 1,
              "query_time" : "2020-08-21 15:18:37",
              "rank" : 4,
              "response_url" : "https://www.baidu.com/s?wd=%E7%9F%A5%E4%B9%8E&ie=utf-8&rn=10&pn=0",
              "title" : "知乎",
              "web_id" : "5",
              "xzh" : null
      }
      ```

      

