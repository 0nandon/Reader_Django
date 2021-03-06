import bs4
from urllib.request import urlopen, Request
from kocrawl.searcher.base_searcher import BaseSearcher
from kocrawl.answerer.base_answerer import BaseAnswerer
from kocrawl.base import BaseCrawler
import re
import datetime


class NewBaseSearcher(BaseSearcher):
    def _make_query(self, location: str, date: str) -> str:
        pass

    def __bs4(self, url, query):

        if query:
            url += query

        out = bs4.BeautifulSoup(urlopen(Request(url, headers=self.headers)).read(), 'html.parser')
        return out

    def _bs4_contents(self, url: str, selectors: list, query: str = ""):
        out = self.__bs4(url, query)

        try:
            crawled = []
            i = 0
            for selector in selectors:
                if selector == '.goodsTxtInfo > p':
                    for s in out.select(selector)[:30]:
                        if i % 6 == 0:
                            crawled.append(s.contents)
                        i += 1
                else:
                    for s in out.select(selector)[:5]:
                        crawled.append(s.contents)
            return crawled
        except Exception:
            return None


class BestSearcher(NewBaseSearcher):
    def __init__(self):
        self.base_url = "http://www.yes24.com"
        self.url = "http://www.yes24.com/24/category/bestseller?CategoryNumber=001&sumgb=09"
        self.CSS = {
            'title': '.goodsTxtInfo > p',
            'info': '.goodsTxtInfo > .aupu'
        }
        self.data_dict = {
            'title': None,
            'info': None,
            'url': None,
        }

    def _make_date(self, month, day=0):
        if day == 0:
            return "&year=2021&month=" + str(month)
        else:
            return "&year=2021&month=" + str(month) + "&day=" + str(day)

    def yes24_search(self, month, day=0) -> dict:
        query = self._make_date(month, day)
        result = self._bs4_contents(self.url,
                                    selectors=[self.CSS['title'], self.CSS['info']],
                                    query=query)

        self.data_dict['title'], self.data_dict['url'] = [], []
        for i in range(5):
            content_url = re.search('<a href="(.+?)">', str(result[i][1])).group(1)
            self.data_dict['url'].append(self.base_url + content_url)
            title1 = str(result[i][0]).replace("[??????] ", "")
            title1 = title1.replace("  ", "")
            title2 = re.search('>(.+?)</a>', str(result[i][1])).group(1)
            self.data_dict['title'].append(title1 + title2)

        self.data_dict['info'] = []
        for i in range(5):
            author = re.search('>(.+?)</a>', str(result[5+i][1])).group(1)

            time = ""
            regex = re.compile(r'\d\d\d\d??? \d\d???')
            matchobj = regex.search(str(result[5+i][4]))
            if matchobj is not None:
                time = matchobj.group()
            self.data_dict['info'].append(author + ' ???, ' + time)

        return self.data_dict


class BestAnswerer(BaseAnswerer):
    def make_answer(self, data_dict, month, day=0, date=""):
        answer = ""
        if date != "":
            answer += "yes 24??? ????????? {} ??????????????? 5?????? ??????????????????.????<br><br>".format(date)
        elif day == 0:
            answer += "yes 24??? ????????? {}??? ??????????????? 5?????? ??????????????????.????<br><br>".format(month)
        else:
            answer += "yes 24??? ????????? {}??? {}??? ??????????????? 5?????? ??????????????????.????<br><br>".format(month, day)

        for i in range(5):
            answer += str(i+1) + ". " + data_dict['title'][i] + " (" + data_dict['info'][i] + ")<br>"
            answer += "????????? ?????? : " + data_dict['url'][i] + "<br>"

        return answer


class BestCrawler(BaseCrawler):
    def __init__(self):
        self.date = {}
        for i in range(1, 13):
            for j in range(1, 32):
                string = "{}??? {}???".format(i, j)
                self.date[string] = (i, j)
        self.month = {}
        for i in range(1, 13):
            string = "{}???".format(i)
            self.month[string] = i

        self.today = datetime.date.today()

    def request(self, date: str):

        try:
            return self.request_debug(date)
        except Exception:
            return BestAnswerer().sorry(
                '??? ????????? ?????????????????? ??? ?????? ?????????.'
            )

    def request_debug(self, date):
        if date in self.date:
            m = self.date[date][0]
            d = self.date[date][1]

            if m >= self.today.month and d > self.today.day:
                raise Exception

            search = BestSearcher().yes24_search(m, d)
            return BestAnswerer().make_answer(search, m, d)
        elif date in self.month:
            m = self.month[date]

            if m > self.today.month:
                raise Exception
            search = BestSearcher().yes24_search(m)
            return BestAnswerer().make_answer(search, m)
        elif date == '??????' or date == '?????????':
            search = BestSearcher().yes24_search(self.today.month, self.today.day)
            return BestAnswerer().make_answer(search, self.today.month, self.today.day, date=date)
        elif date == '??????':
            yesterday = self.today - datetime.timedelta(days=1)
            search = BestSearcher().yes24_search(yesterday.month, yesterday.day)
            return BestAnswerer().make_answer(search, yesterday.month, yesterday.day, date=date)
        elif date == '?????? ???':
            search = BestSearcher().yes24_search(self.today.month)
            return BestAnswerer().make_answer(search, self.today.month, date=date)
        elif date == '?????? ???':

            if self.today.month == 1:
                raise Exception

            search = BestSearcher().yes24_search(self.today.month-1)
            return BestAnswerer().make_answer(search, self.today.month-1, date=date)
        elif date == '?????? ???':
            last = self.today - datetime.timedelta(weeks=1)
            search = BestSearcher().yes24_search(last.month, last.day)
            return BestAnswerer().make_answer(search, last.month, last.day, date=date)
        else:
            raise Exception



def krawl(request):
    a = BestSearcher()
    b = a.yes24_search(3, 17)
    BestAnswerer().make_answer(b, 3, 17)
    # out = a.__bs4(url, "")
    # print(out)
