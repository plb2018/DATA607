# -*- coding: utf-8 -*-

# based on "First attempt: Original Code" by Iden
# Web Scraper for Indeed job postings
# Source: Michael Salmon's Medium post
# URL: https://medium.com/@msalmon00/web-scraping-job-postings-from-indeed-96bd588dcb4b


import requests
import bs4
from bs4 import BeautifulSoup
import os
import pandas as pd
import time


max_results_per_city = 100


city_set = ["New+York+NY", "Seattle+WA", "San+Francisco+CA", "Washington+DC", "Atlanta+GA",
            "Boston+MA", "Austin+TX", "Cincinnati+OH", "Pittsburgh+PA"]

columns = ["city", "job_title", "company_name", "location", "summary", "salary"]

sample_df = pd.DataFrame(columns = columns)

df = pd.DataFrame(columns = columns)

links = []

base_url = "https://www.indeed.com/"

for city in city_set:
    print city
    for start in range(0, max_results_per_city, 10):
        page = requests.get("http://www.indeed.com/jobs?q=data+scientist&l=" + str(city) + "&start=" + str(start))
        time.sleep(1)
        soup = BeautifulSoup(page.text, "lxml", from_encoding = "utf-8")

        #collect links into a list - will be used later to get summary_full
        for div in soup.find_all(name = "div", attrs = {"class":"row"}):
            for a in div.find_all(name = "a", attrs = {"data-tn-element":"jobTitle"}):
                links.append(base_url+a["href"])
                

        #pull the details
        for div in soup.find_all(name = "div", attrs = {"class":"row"}):
            num = (len(sample_df) + 1)          # Row num for df
            job_post = []                       # New job posting
            job_post.append(city)               # Append city from city_set       
            for a in div.find_all(name = "a", attrs = {"data-tn-element":"jobTitle"}):
                job_post.append(a["title"])     # Append job title
            company = div.find_all(name = "span", attrs = {"class":"company"})
            if len(company) > 0:                # Get company name
                for b in company:
                    job_post.append(b.text.strip())
            else:
                sec_try = div.find_all(name = "span", attrs = {"class":"result-link-source"})
                for span in sec_try:
                    job_post.append(span.text)
            c = div.findAll("span", attrs = {"class":"location"})
            for span in c:
                job_post.append(span.text)      # Append location of job
            d = div.findAll("span", attrs = {"class":"summary"})
            for span in d:                      # Append job summary
                job_post.append(span.text.strip())
            try:                                # Get job salary, if any
                job_post.append(div.find("nobr").text)
            except:
                try:
                    div_two = div.find(name = "div", attrs = {"class":"sjcl"})
                    div_three = div_two.find("div")
                    job_post.append(div_three.text.strip())
                except:
                    job_post.append("")
            sample_df.loc[num] = job_post

#add the links to the df
sample_df['link'] = links

#add a placeholder col for the full summary
sample_df['summary_full'] = "" 


#iterate over the sample_df and access the save links
for i,row in sample_df.iterrows():

    #a progress report...
    if i%10 == 0:
        print str(i) + "of" + str(sample_df.shape[0])

    summary = []
    page2 = requests.get(row['link'])
    soup2 = BeautifulSoup(page2.text, "html.parser")
    time.sleep(1)
    d = soup2.findAll("span", attrs = {"class":"summary"})
    for span in d:
        #clean up the data a bit (remove spaces & whitespace etc)
        data = span.text.strip()
        data = os.linesep.join([s for s in data.splitlines() if s])
        data =data.replace("\r","")
        data = data.replace("\n","")
        summary.append(data)


    #add the full summary to the sample_df
    sample_df['summary_full'].loc[i] = summary  

#write it all to file using "|" delim
sample_df.to_csv("indeed_sample.csv",sep="|",encoding = "utf-8")

