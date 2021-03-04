from django.urls import path
from django.conf.urls import url
from App import views

urlpatterns = [
    path('', views.App, name='App'),
    path('join', views.join, name='join'),
    path('sdg', views.sdg, name='sdg'),
    path('lda', views.lda, name='lda'),
    path('module/<str:pk>', views.module, name='module'),
    path('publication/<str:pk>', views.publication, name='publication'),
    path('exportMod', views.export_modules_csv, name='export_modules_csv'),
    path('exportPub', views.export_publications_csv,name='export_publications_csv'),
]
