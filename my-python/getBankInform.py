import re
from urllib.request import Request, urlopen
import pandas as pd
from bs4 import BeautifulSoup
import warnings
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")


def getSoupFrom(url):
    req = Request(
        url=url,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    webpage = urlopen(req).read()
    condaStr = webpage.decode("utf8")

    soup = BeautifulSoup(condaStr, 'lxml')
    return soup


def getOCBCInform(url):

    def getDataFrom(parsedTable):
        data = []
        for row in parsedTable.find_all('tr'):
            collect = []
            for st in row.find_all('strong'):
                collect.append(' '.join(st.stripped_strings))
            if collect != []:
                data.append(collect)
        df = pd.DataFrame(data[1:], columns=['Year', 'Interest Rates'])
        return df

    def getOtherDataFrom(parsedData):
        otherDf = pd.DataFrame([], columns=["Min Loan Size", "fixed rate",
                                            "sora rate",
                                            "floating rate",
                                            "fixed and sora rate"])

        otherDf["fixed rate"], otherDf["sora rate"], \
        otherDf["floating rate"], otherDf["fixed and sora rate"] = \
            [False], [True], [False], [False]
          
        for div in parsedData.find_all('div'):
            for p in div.find_all('p'):
                if "Minimum loan amount for Singapore private home" in p:
                    otherDf["Min Loan Size"] = p.find_next("p").text

        return otherDf

    soup = getSoupFrom(url)
    tables = soup.find_all("table")
    df = pd.DataFrame([])
    for table in tables:
        for th in table.find_all('th'):
            if "SORA" in ''.join(th.stripped_strings):
                df = getDataFrom(table)
                break
    otherDf = getOtherDataFrom(soup)
    return df, otherDf


def getUOBInform(url):

    def getDataFrom(parsedTable):
        data = []
        otherData = []
        for row in parsedTable.find_all('tr'):
            collect = []
            if "Year" in row.text:
                for td in row.find_all('td'):
                    collect.append(' '.join(td.stripped_strings))
                data.append(collect)
            else:
                for td in row.find_all('td'):
                    collect.append(' '.join(td.stripped_strings))
                otherData.append(collect)

        otherData[-2][1] += " "+otherData[-1][0]

        df = pd.DataFrame(data).iloc[:, :2]
        df.columns = ["Year", "Interest Rates"]
        otherDf = pd.DataFrame(otherData[1:-1]).iloc[:, :2]
        otherDf = otherDf.set_index(0).T.reset_index(drop=True)

        return df, otherDf

    def getPointFrom(otherDf, parsedPoints):
        otherDf["fixed rate"], otherDf["sora rate"], \
            otherDf["floating rate"], otherDf["fixed and sora rate"] = \
            [False], [False], [False], [False]

        for li in parsedPoints:
            if "SORA" and "fixed-rate" and "Combination" in li.text:
                otherDf["fixed and sora rate"] = [True]
            elif "Fixed-rate" in li.text:
                otherDf["fixed rate"] = [True]
            elif "Floating rate" in li.text:
                otherDf["floating rate"] = [True]
            elif "SORA" in li.text:
                otherDf["sora rate"] = [True]
        return otherDf

    soup = getSoupFrom(url)
    tables = soup.find_all("table")
    points = soup.find_all('li')
    df = pd.DataFrame([])
    for table in tables:
        for td in table.find_all('td'):
            if "SORA" in ''.join(td.stripped_strings):
                df, otherDf = getDataFrom(table)
                break
    otherDf = getPointFrom(otherDf, points)

    return df, otherDf


def saveJsonTo(dictDf, fileName='./DataInJson/BankInform.json'):
    df = pd.DataFrame.from_dict(dictDf.items())
    df.to_json(fileName, orient="records")


def main():
    ocbcurl = "https://www.ocbc.com/personal-banking/loans/new-purchase-of-hdb-private-property?cid=Mass:loans:HomeLoan:Tactical:Acquisition:Oct-Nov:2022:sem:Google:PPT-Brand:Responsive-Search-Ad:ocbc%20house%20loan:&gclid=Cj0KCQiA1NebBhDDARIsAANiDD2yEqhrplGyQp6C-YxxoH73i_dR7MYWDXqQfLGAxqm1TljudbtZwUMaAlyZEALw_wcB&gclsrc=aw.ds"
    uoburl = "https://www.uob.com.sg/personal/borrow/property/mortgage-options/private-home-loan.page"
    ocbcDf, ocbcOtherDf = getOCBCInform(ocbcurl)
    uobDf, uobOtherDf = getUOBInform(uoburl)

    dictDf = {"ocbc": {"rate": ocbcDf, "other": ocbcOtherDf},
              "uob": {"rate": uobDf, "other": uobOtherDf}}
    saveJsonTo(dictDf)
    return


if __name__ == '__main__':
    main()
