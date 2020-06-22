"""
 Created on 8:15 PM 6/17/2020 using PyCharm
 
 @author: Raj
"""

import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
from selenium import webdriver
from urllib.request import urlopen as uReq

app = Flask(__name__)


@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")


@app.route('/review', methods=['POST', 'GET'])  # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchJob = request.form['content']
            #searchProduct = request.form['content'].replace(" ", "")
            if len(searchJob.strip()) == 0:
                return "Please enter job profile to list down Jobs"
            else:
                # Chrome driver
                chrome_options = webdriver.ChromeOptions()
                chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--no-sandbox")
                driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
                # Now you can start using Selenium

                url = "https://www.monsterindia.com/srp/results?query=" + searchJob
                driver.get(url)
                driver.encoding = 'utf-8'
                driver.implicitly_wait(30)
                source = driver.page_source
                html = bs(source,'html.parser')

                bigBox = html.find_all('div', {'class': 'card-apply-content'})
                jobs = []
                for job in bigBox:
                    try:
                        jobLink = 'https:'+ job.find('div',{'class':'job-tittle'}).h3.a['href']
                    except Exception as e:
                        jobLink = "No Job Url"
                        print(f"ERROR - Ref to job url {jobLink} - {e}")
                    try:
                        jobTitle = job.find('div',{'class':'job-tittle'}).h3.a.text
                    except Exception as e:
                        jobTitle = "No Job Title"
                        print(f"ERROR - Ref to job title {jobTitle} - {e}")
                    try:
                        companyName = job.find('div',{'class':'job-tittle'}).span.a.text
                    except Exception as e:
                        companyName = "No Company Name"
                        print(f"ERROR - Ref to company name {companyName} - {e}")
                    try:
                        location = job.find('div',{'class':'job-tittle'}).div.div.span.small.text.strip()
                    except Exception as e:
                        location = "No Location"
                        print(f"ERROR - Ref to location {location} - {e}")
                    try:
                        workExp = job.find('div', {'class': 'job-tittle'}).find('div', {'class': 'searctag row'}) \
                            .find('div', {'class': 'exp col-xxs-12 col-sm-3 text-ellipsis'}).small.text.strip()
                    except Exception as e:
                        workExp = "No Exp Detail"
                        print(f"ERROR - Ref to work exp {workExp} - {e}")
                    try:
                        salary = job.find('div', {'class': 'job-tittle'}).find('div', {'class': 'searctag row'}) \
                            .find('div', {'class': 'package col-xxs-12 col-sm-4 text-ellipsis'}).small.text.strip()
                    except Exception as e:
                        salary = "No Salary Detail"
                        print(f"ERROR - Ref to salary {salary} - {e}")
                    try:
                        job_description = job.p.text
                    except Exception as e:
                        job_description = "No Job Description"
                        print(f"ERROR - Ref to job description {job_description} - {e}")
                    try:
                        skillBox = job.find('p',{'class':'descrip-skills'}).findAll('span',{'class':'grey-link'})
                        skills = []
                        for skill in skillBox:
                            sk = skill.a.text.strip()
                            sk = sk.split(",")[0].strip()
                            skills.append(sk)
                        skills = str(skills)[1:-1]
                    except Exception as e:
                        skills = "No Skills Details"
                        print(f"ERROR - Ref to job skills {skills} - {e}")
                    try:
                        jobDict = {"Job Link": jobLink, "Job Title": jobTitle, "Company": companyName,
                                  "Location": location, "Work Exp":workExp, "Salary":salary,
                                   "Job Description":job_description, "Skills":skills}
                        jobs.append(jobDict)
                    except Exception as e:
                        print(f"ERROR - Ref to job details {jobDict} - {e}")
                if len(jobs) == 0:
                    return "Please enter job profile for best results..!!"
                bigBoxFooter = html.find_all('div', {'class': 'card-footer apply-footer no-bdr'})
                jobs1 =[]
                for job in bigBoxFooter:
                    try:
                        jobPosted = job.find('div',{'class':'posted-update pl5'}).span.text.strip()
                    except Exception as e:
                        jobPosted = "No Post Date"
                        print(f"ERROR - Ref to job posted {jobPosted} - {e}")
                    try:
                        jobDict1 = {"Job Posted": jobPosted}
                        jobs1.append(jobDict1)
                        #print("jobDict1",jobDict1)
                    except Exception as e:
                        print(f"ERROR - Ref to job details1 {jobDict1} - {e}")
                #logic to combine above two list of dict into a final list of dict: jobList with all required keys & values
                j = 0
                jobList = []
                for i in jobs:
                    i[list(jobs1[j].keys())[0]] = list(jobs1[j].values())[0]
                    j += 1
                jobList = jobs




            return render_template('results.html', reviews=jobList[0:(len(jobList) - 1)])
        except Exception as e:
            print('The Exception message is: ', e)
            return 'Please enter job profile for best results..!!'
    # return render_template('results.html')

    else:
        return render_template('index.html')

port = int(os.getenv("PORT"))
if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=5000)
    app.run(host='0.0.0.0', port=port)
    #app.run(host='127.0.0.1', port=8001, debug=True)
