# weibopic-crawler
A simple Python program aiming to fetch images on Weibo.

Dependencies:
- requests

```bash
pip3 install -r requirements.txt
```

Usage:
```bash
python3 crawl.py [-f] [--retweet] ID N
```
- `-f`, `--force`: Clear cache before downloading
- `--retweet`: Include retweets
- `ID`: personal url codename (`liaoxuefeng`) or number ID (`1658384301`)
- `N`: Maximum page count
