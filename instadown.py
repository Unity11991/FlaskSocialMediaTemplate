import requests
from bs4 import BeautifulSoup
from sqlalchemy.engine import url


def getdata(url=''):
    result = requests.get(url).text
    soup = BeautifulSoup(result, "html.parser")
    video_url = soup.find('meta', attrs={'property': 'og:video'})['content']
    return video_url


if __name__ == '__main__':
    print(getdata(url))
