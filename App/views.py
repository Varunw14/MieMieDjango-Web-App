from django.shortcuts import render, redirect
from .models import Module, Publication
from django.views import View
from .forms import ModuleForm
from django.contrib import messages
from django.db.models import Q
import pyodbc, json, os
from django.http import HttpResponse
import csv
import pickle
import gensim
import pandas as pd


Module_CSV_Data = None
Publication_CSV_Data = None
global_context = {}
global_display_limit = 10
UCL_AffiliationID = "60022148"


def App(request):
    global Module_CSV_Data
    global Publication_CSV_Data
    global global_context

    all_modules = Module.objects.all
    all_publications = Publication.objects.all()[:global_display_limit]

    if request.method == "POST":
        updatePublicationsFromJSON(request)
        updateModuleData(request)
        return redirect('App')

    form = {"modBox": "unchecked", "pubBox": "unchecked"}
    len_mod = Module.objects.count()
    len_pub = Publication.objects.count()
    context = {
        'mod': all_modules,
        'pub': all_publications,
        'len_mod': len_mod,
        'len_pub': len_pub,
        'len_total': len_mod + len_pub,
        'form': form
    }

    if request.method == 'GET':
        query = request.GET.get('q')
        form = getCheckBoxState(request, form)
        if query is not None and query != '' and len(query) != 0:
            c = returnQuery(request, form, query, all_modules, all_publications)
            return render(request, 'index.html', c)

        else:
            Module_CSV_Data = None
            Publication_CSV_Data = None

    len_mod = Module.objects.count()
    len_pub = Publication.objects.count()
    context = {
        'mod': all_modules,
        'pub': all_publications,
        'len_mod': len_mod,
        'len_pub': len_pub,
        'len_total': len_mod + len_pub,
        'form': form
    }
    Module_CSV_Data = None
    Publication_CSV_Data = None
    global_context = context
    return render(request, 'index.html', context)

def getDB():
    # SERVER LOGIN DETAILS
    server = 'miemie.database.windows.net'
    database = 'MainDB'
    username = 'miemie_login'
    password = 'e_Paswrd?!'
    driver = '{ODBC Driver 17 for SQL Server}'
    # CONNECT TO DATABASE
    myConnection = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server +
                                  ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    curr = myConnection.cursor()
    curr.execute("SELECT * FROM [dbo].[ModuleData]")
    result = curr.fetchall()
    return result

def updateModuleData(request):
    new_data = getDB()
    for i in new_data:
        obj, created = Module.objects.get_or_create(Department_Name=i[0], Department_ID=i[1], Module_Name=i[2], Module_ID=i[3], Faculty=i[4], Credit_Value=i[5], Module_Lead=i[6], Catalogue_Link=i[7], Description=i[8])

def clearEmptySDG_assignments():
    Publication.objects.filter(assignedSDG__isnull=True).delete()

def updatePublicationsFromJSON(request):
    files_directory = "ALL_SCAPERS/SCOPUS/GENERATED_FILES/"
    allFileNames = os.listdir(files_directory)
    for i in allFileNames:
        with open(files_directory + i) as json_file:
            data_ = json.load(json_file)
            if data_:
    
                obj, created = Publication.objects.get_or_create(title=data_['Title'])
                obj.data = data_
                obj.save()

def getCheckBoxState(request, form):
    if request.GET.get('modBox') == "clicked":
        form['modBox'] = "checked"
    else:
        form['modBox'] = "unchecked"
    if request.GET.get('pubBox') == "clicked":
        form['pubBox'] = "checked"
    else:
        form['pubBox'] = "unchecked"
    return form

def moduleSearch(request, query, all_publications, form):
    lookups = Q(Department_Name__icontains=query) | Q(Department_ID__icontains=query) | Q(Module_Name__icontains=query) | Q(Module_ID__icontains=query) | Q(
        Faculty__icontains=query) | Q(Module_Lead__icontains=query) | Q(Description__icontains=query)
    myFilter = Module.objects.filter(lookups).distinct()
    len_mod = myFilter.count()
    len_pub = Publication.objects.count()
    return {
        'mod': myFilter,
        'pub': all_publications,
        'submitbutton': request.GET.get('submit'),
        'len_mod': len_mod,
        'len_pub': len_pub,
        'len_total': len_mod + len_pub,
        'form': form
    }

def publicationSearch(request, query, all_modules, form):
    myFilter = Publication.objects.filter(data__icontains=query).distinct()
    len_mod = Module.objects.count()
    len_pub = myFilter.count()
    return {
        'mod': all_modules,
        'pub': myFilter,
        'submitbutton': request.GET.get('submit'),
        'len_mod': len_mod,
        'len_pub': len_pub,
        'len_total': len_mod + len_pub,
        'form': form
    }

def allSearch(request, query, all_modules, all_publications, form):
    moduleResults = moduleSearch(request, query, all_modules, form)['mod']
    publicationResults = publicationSearch(request, query, all_modules, form)['pub']
    len_mod = moduleResults.count()
    len_pub = publicationResults.count()
    return {
        'mod': moduleResults,
        'pub': publicationResults,
        'submitbutton': request.GET.get('submit'),
        'len_mod': len_mod,
        'len_pub': len_pub,
        'len_total': len_mod + len_pub,
        'form': form
    }

def returnQuery(request, form, query, all_modules, all_publications):
    global Module_CSV_Data
    global Publication_CSV_Data
    global global_context

    if form['modBox'] == "checked" and form['pubBox'] == "unchecked":  # if only modules
        context = moduleSearch(request, query, all_publications, form)
        Module_CSV_Data = context["mod"]
        Publication_CSV_Data = None
    if form['modBox'] == "unchecked" and form['pubBox'] == "checked": # if only publications
        context = publicationSearch(request, query, all_modules, form)
        Module_CSV_Data = None
        Publication_CSV_Data = context["pub"]
    elif form['modBox'] == "checked" and form['pubBox'] == "checked":  # if both
        context = allSearch(request, query, all_modules, all_publications, form)
        Module_CSV_Data = context["mod"]
        Publication_CSV_Data = context["pub"]
    global_context = context
    return context

def lda(request):
    return render(request, "lda.html", {})

def join(request):
    if request.method == "POST":
        form = ModuleForm(request.POST or None)
        if form.is_valid():
            form.save()
        else:
            saved_data = {
                "Department_Name": request.POST['Department_Name'],
                "Department_ID": request.POST['Department_ID'],
                "Module_Name": request.POST['Module_Name'],
                "Module_ID": request.POST['Module_ID'],
                "Faculty": request.POST['Faculty'],
                "Credit_Value": request.POST['Credit_Value'],
                "Module_Lead": request.POST['Module_Lead'],
                "Catalogue_Link": request.POST['Catalogue_Link'],
                "Description": request.POST['Description']
            }
            messages.success(request, ("There was an error in your form! Please try again."))
            return render(request, 'join.html', saved_data)

        messages.success(request, ("Your form has been submitted successfully!"))
        return redirect('App')

    else:
        return render(request, 'join.html', {})

def processForSDG(doi_searched):
    publicationData = pd.DataFrame(columns=['DOI', 'Description'])
    p = Publication.objects.all()
    for i in p:
        data = json.dumps(i.data)
        data = json.loads(data)
        doi = data['DOI']
        if doi_searched == doi:
            concatDataFields = i.title
            if data['Abstract']:
                concatDataFields += data['Abstract']
            if data['AuthorKeywords']:
                concatDataFields += " ".join(data['AuthorKeywords'])
            if data['IndexKeywords']:
                concatDataFields += " ".join(data['IndexKeywords'])
            if data['SubjectAreas']:
                subjectName = [x[0] for x in data['SubjectAreas']]
                concatDataFields += " ".join(subjectName)
            rowDataFrame = pd.DataFrame([[doi, concatDataFields]], columns=publicationData.columns)
            publicationData = publicationData.append(rowDataFrame, verify_integrity=True, ignore_index=True)
    return publicationData

def loadSDG_Data_PUBLICATION():
    files_directory = "ALL_SCAPERS/sdgAssignments.json"
    with open(files_directory) as json_file:
        data_ = json.load(json_file)
        for i in data_:
            obj = Publication.objects.get(title=data_[i]['Title'])
            obj.assignedSDG = data_[i]
            obj.save()

def loadSDG_Data_MODULES():
    files_directory = "ALL_SCAPERS/training_results.json"
    with open(files_directory) as json_file:
        data_ = json.load(json_file)['Document Topics']
        for module in data_:
            weights = data_[module]
            module_SDG_assignments = {}
            module_SDG_assignments["Module_ID"] = module
            for i in range(len(weights)):
                weights[i] = weights[i].replace('(', '').replace(')', '').replace('%', '').replace(' ', '').split(',')
                sdgNum = weights[i][0]
                module_SDG_assignments[sdgNum] = float(weights[i][1])

            obj = Module.objects.get(Module_ID=module)
            obj.assignedSDG = module_SDG_assignments
            obj.save()

def sdg(request):
    form = {"modBox": "unchecked", "pubBox": "unchecked"}
    context = {
        'pub': Publication.objects.all()[:global_display_limit],
        'mod': Module.objects.all()[:global_display_limit],
        'lenPub': Publication.objects.count(),
        'lenMod': Module.objects.count(),
        'form': getCheckBoxState(request, form)
    }

    # Update the database with new sdg assignments
    if request.method == "POST":
        # loadSDG_Data_PUBLICATION()
        # loadSDG_Data_MODULES()
        pass

    if request.method == 'GET':
        query = request.GET.get('b')
        if query is not None and query != '' and len(query) != 0:
            context = returnQuery(request, form, query, context['mod'], context['pub'])
            context['lenPub'] = context['pub'].count()
            context['lenMod'] = context['mod'].count()

    return render(request, 'sdg.html', context)

def module(request, pk):
    try:
        module = Module.objects.get(id=pk)
    except Module.DoesNotExist:
        raise ("Module does not exist")
    return render(request, 'module.html', {'mod': module})

def publication(request, pk):
    try:
        publication = Publication.objects.get(id=pk)
    except Publication.DoesNotExist:
        raise ("Publication does not exist")
    return render(request, 'publication.html', {'pub': publication})

def export_modules_csv(request):
    global Module_CSV_Data
    global global_context
    response = HttpResponse(content_type='text/csv')

    if not Module_CSV_Data:
        messages.success(request, ("No modules to export! Please try again."))
        return render(request, 'index.html', global_context)
        
    response['Content-Disposition'] = 'attachment; filename="modules.csv"'

    try:
        writer = csv.writer(response)
        writer.writerow(["Department_Name", "Department_ID", "Module_Name", "Module_ID", "Faculty", "Credit_Value", "Module_Lead", "Catalogue_Link", "Description"])
        modules = Module_CSV_Data.values_list("Department_Name", "Department_ID", "Module_Name", "Module_ID", "Faculty", "Credit_Value", "Module_Lead", "Catalogue_Link", "Description")
        for module in modules:
            writer.writerow(module)
    except:
        messages.success(request, ("No modules to export! Please try again."))
        return render(request, 'index.html', global_context)
    
    return response

def export_publications_csv(request):
    global Publication_CSV_Data
    global global_context

    response = HttpResponse(content_type='text/csv')

    if not Publication_CSV_Data:
        messages.success(request, ("No publications to export! Please try again."))
        return render(request, 'index.html', global_context)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="publications.csv"'

    try:
        writer = csv.writer(response)
        writer.writerow(["Title", "EID", "DOI", "Year", "Source", "Volume", "Issue", "Page-Start", "Page-End", "Cited By",
                         "Link", "Abstract", "Author Keywords", "Index Keywords", "Dcoument Type", "Publication Stage", "Open Access", "Subject Areas", "UCL Authors Data", "Other Authors Data"])
    except:
        messages.success(request, ("No publications to export! Please try again."))
        return render(request, 'index.html', global_context)
    
    publications = Publication_CSV_Data.values_list("data")
    for paper in publications:
        detail = json.dumps(paper)
        all_contents = json.loads(detail)[0]
        title = all_contents['Title']
        EID = all_contents['EID']
        DOI = all_contents['DOI']
        Year = all_contents['Year']
        Source = all_contents['Source']
        Volume = all_contents['Volume']
        Issue = all_contents['Issue']
        PageStart = all_contents['PageStart']
        PageEnd = all_contents['PageEnd']
        CitedBy = all_contents['CitedBy']
        Link = all_contents['Link']
        Abstract = all_contents['Abstract']
        AuthorKeywords = all_contents['AuthorKeywords']
        if AuthorKeywords:
            AuthorKeywords = ','.join(AuthorKeywords)
        IndexKeywords = all_contents['IndexKeywords']
        if IndexKeywords:
            IndexKeywords = ','.join(IndexKeywords)
        DocumentType = all_contents['DocumentType']
        PublicationStage = all_contents['PublicationStage']
        OpenAccess = all_contents['OpenAccess']
        SubjectAreas = all_contents['SubjectAreas']
        temp = []
        if SubjectAreas:
            for area in SubjectAreas:
                temp.append(area[0])
        SubjectAreas = ','.join(temp)
        AuthorData = all_contents['AuthorData']
        UCLAuthorsData = []
        OtherAuthorsData = []
        if AuthorData:
            for id_ in AuthorData:
                name = AuthorData[id_]['Name']
                affiliationID = AuthorData[id_]['AffiliationID']
                affiliationName = AuthorData[id_]['AffiliationName']
                if affiliationID  == UCL_AffiliationID:
                    UCLAuthorsData.append(name + "(" + affiliationName + ")")
                else:
                    if name and not affiliationName:
                        OtherAuthorsData.append(','.join([name, ""]))
                    if not name and not affiliationName:
                        OtherAuthorsData.append("")
                    if name and affiliationName:
                        OtherAuthorsData.append(name + "(" + affiliationName + ")")
                    
        UCLAuthorsData = ','.join(UCLAuthorsData)
        OtherAuthorsData = ','.join(OtherAuthorsData)

        writer.writerow([title, EID, DOI, Year, Source, Volume, Issue, PageStart, PageEnd, CitedBy, Link, Abstract, AuthorKeywords,
                         IndexKeywords, DocumentType, PublicationStage, OpenAccess, SubjectAreas, UCLAuthorsData, OtherAuthorsData])

    return response
