import django
import glob
import os
import sys
import pybliometrics.scopus as ok
import pandas as pd
import json
import pathlib
import csv
import math
import numpy as np
import os


from App.models import Publication

f = open("App/ALL_SCAPERS/SCOPUS/log.txt", "a")

class GetScopusData():

    def __init__(self):
        self.rps_data_file = "App/ALL_SCAPERS/SCOPUS/cleaned_RPS_export_2015.csv"
        self.generated_data = "App/ALL_SCAPERS/SCOPUS/GENERATED_FILES/"

    def progress(self, count, total, custom_text, suffix=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)

        sys.stdout.write('[%s] %s%s %s %s\r' %
                         (bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def getDOIs(self, columns, limit=None):
        if not limit:
            return pd.read_csv(self.rps_data_file)[columns]
        return pd.read_csv(self.rps_data_file)[columns].head(limit)

    def getInfo(self, scopusID):
        valid = True
        try:
       	    scopus = ok.AbstractRetrieval(scopusID, view='FULL')
        except Exception as e:
            # f.write("Invalid DOI: " + scopusID + "\n")
            f.write(str(e) + "\n")

            valid = False
            return "invalid"

        if valid:
            authors = scopus.authors
            author_group = scopus.authorgroup
            title = scopus.title
            try:
                date = int(scopus.coverDate[:4])
            except:
                date = None
            source = scopus.srctype
            volume = scopus.volume
            try:
                issue = int(scopus.issueIdentifier)
            except:
                issue = None
            try:
                pageStart = int(scopus.startingPage)
            except:
                pageStart = None
            try:
                pageEnd = int(scopus.endingPage)
            except:
                pageEnd = None
            citedBy = scopus.citedby_count
            doi = scopus.doi
            link = scopus.scopus_link
            affiliations = scopus.affiliation
            abstract = scopus.abstract
            authorKeywords = scopus.authkeywords
            indexKeywords = scopus.idxterms
            docType = scopus.aggregationType
            try:
                openAccess = int(scopus.openaccess)
            except:
                openAccess = None
            source = scopus.sourcetitle_abbreviation
            eid = scopus.eid

            # Additional data
            subjectAreas = scopus.subject_areas

            return {"Authors": authors, "AuthorGroup": author_group, "Title": title, "Year": date, "Source": source,
                    "Volume": volume, "Issue": issue, "Art.No": None, "PageStart": pageStart,
                    "PageEnd": pageEnd, "CitedBy": citedBy, "DOI": doi, "Link": link,
                    "Affiliations": affiliations, "Abstract": abstract, "AuthorKeywords": authorKeywords,
                    "IndexKeywords": indexKeywords, "DocumentType": docType, "PublicationStage": None,
                    "OpenAccess": openAccess, "Source": source, "EID": eid, "SubjectAreas": subjectAreas}

    def formatData(self, data):
        authorData = {}
        # if "AuthoGroup" in data:
        if data['AuthorGroup']:
            for i in data['AuthorGroup']:
                affiliationID = i[0]
                affiliationName = i[2]
                authorID = i[7]
                authorName = i[8]
                author = {"Name": authorName, "AuthorID": authorID,
                          "AffiliationID": affiliationID, "AffiliationName": affiliationName}
                authorData[authorID] = author
            del data['AuthorGroup']
            del data['Authors']
            del data['Affiliations']
            data['AuthorData'] = authorData
            return data
        return None

    def cleanerFileReadings(self, limit):
        one_researcher = self.getDOIs(["DOI"], limit)
        doi_list = list(one_researcher["DOI"])
        doi = set(doi_list)
        result = set()

        for i in doi:
            if i is np.nan:
                continue
            if ',' in i:
                temp = i.split(',')
                for j in temp:
                    result.add(j)
            else:
                result.add(i)

        files_directory = "App/ALL_SCAPERS/SCOPUS/GENERATED_FILES/"
        DIR = 'App/ALL_SCAPERS/SCOPUS/GENERATED_FILES/'
        num_of_files = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
        already_scraped_DOI = []

        allFileNames = os.listdir(files_directory)
        for i in allFileNames:
            with open(files_directory + i) as json_file:
                data_ = json.load(json_file)
                if data_:
                    already_scraped_DOI.append(data_['DOI'])
        exists = 0
        notexists = 0
        new_doi = set()
        for elem in result:
            if elem in already_scraped_DOI:
                exists += 1
            else:
                new_doi.add(elem)
                notexists += 1
        print("Already existed", exists)
        print("New doi's", notexists)
        print()
        return new_doi

    def renameAllFiles(self):
        files_directory = "App/ALL_SCAPERS/SCOPUS/GENERATED_FILES/"
        for path in pathlib.Path(files_directory).iterdir():
            if path.is_file():
                with open(path) as json_file:
                    data_ = json.load(json_file)
                    if data_:
                        old_name = path.stem
                        old_extension = path.suffix
                        directory = path.parent
                        new_name = data_['EID'] + old_extension
                        path.rename(pathlib.Path(directory, new_name))

    def pushToDB(self, data):
        if data:
            obj, created = Publication.objects.get_or_create(title=data['Title'])
            obj.data = data
            obj.save()

    def createAllFiles(self, limit):
        data = self.cleanerFileReadings(limit=limit)
        l = len(data)

        counter = 1
        for i in data:
            data_dict = self.getInfo(i)
            if data_dict != "invalid":
                self.progress(counter, l, "writing files")
                f.write("Written " + str(counter) + "/" +l + " files " + "DOI: " + i + "\n")
                reformatted_data = self.formatData(data_dict)
                self.pushToDB(reformatted_data)
                with open("App/ALL_SCAPERS/SCOPUS/GENERATED_FILES/" + data_dict["EID"] + '.json', 'w') as outfile:
                    json.dump(reformatted_data, outfile)
                counter += 1
        print()
        f.write("\nDONE")
        f.close()
