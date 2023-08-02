target = {
"22": ["computing-internet"],
"21/20/19/18/17/16/15/14/13": ["inventors", "entrepreneurs", "visionaries", "humanitarians", "pioneers"],
"12": ["web", "computing"],
"11/10/09": ["web", "computing", "communications"],
"08/07/06/05/04/03/02/99": ["computing"]
}

url_head = "https://www.technologyreview.com/innovators-under-35/"
url_tails = []
for k,tags in target.items():
    for year in k.split("/"):
        for tag in tags:
            url_tails.append(f"{tag}-{1999 if year=='99' else '20'+year}")

import urllib.request

for url_tail in url_tails:
    req = urllib.request.Request(url_head + url_tail)
    print(req.full_url)
    try:
        with urllib.request.urlopen(req) as response:
            the_page = response.read()
            with open(url_tail+".html", "wb") as f:
                f.write(the_page)
    except Exception as e:
        print(e)

import re

for url_tail in url_tails:
    print(url_tail+".html")
    with open(url_tail+".html", "r") as f:
        content = f.read()
        m = re.search("window.__PRELOADED_STATE__ = (.*false}});", str(content))
        if not m:
            print("something wrong")
            continue
        with open(url_tail+".json","w") as j:
            j.write(m.group(1))

import json
import pandas as pd

df = None

for url_tail in url_tails:
    with open(url_tail+".json", "r", encoding="utf-8") as f:
        content = f.read()
        data = json.loads(content)
        data = data['components']['page']['/innovators-under-35/'+url_tail]
    try:
        for d in data:
            if d['name'] == 'body':
                data = d['children']
                break
        for d in data:
            if d['name'] == 'innovator':
                record = {
                    "title": d['config']['title'],
                    "subtitle": d['config']['subtitle'],
                    "age": d['config']['age'],
                    "affiliation": d['config']['affiliation'],
                    "from": url_tail,
                }
                for c in d['children']:
                    if c['name'] == 'gutenberg-content':
                        for gc in c['children']:
                            if gc['name'] == 'html':
                                record['content'] = gc['config']['content']
                            break
                        break
                record = pd.DataFrame(data=record, index=[0])
                df = record if df is None else pd.concat([df, record])
    except Exception as e:
        print(e)

df.to_csv("data.csv", index=False)
df.to_html("data.html", index=False, escape=False)
