import requests
import pandas as pd

url = 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7432275/table/ioi200047t2/?report=objectonly'

header = {
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
  "X-Requested-With": "XMLHttpRequest"
}

r = requests.get(url, headers=header)

dfs = pd.read_html(r.text)

print(dfs)
