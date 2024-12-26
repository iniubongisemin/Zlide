from django.urls import path
from . import views
# from .views import RenderTemplateView

urlpatterns = [
    path('generatezlide/', views.GenerateZlideView.as_view(), name='generatezlide'),
    path('savezlide/', views.SaveZlideView.as_view(), name='savezlide'),
    path('downloadzlide/', views.DownloadZlideView.as_view(), name='downloadzlide'),
    path('openzlide/<str:title>/', views.GetZlideView.as_view(), name='openzlide'),
    path('editzlide/<str:title>/', views.EditZlideView.as_view(), name='editzlide'),
    path('deletezlide/', views.DeleteZlideView.as_view(), name='deletezlide'),
    # path('templateone/', views.TemplateOneView.as_view(), name='templateone'),
    # path('templatetwo/', views.TemplateTwoView.as_view(), name='templatetwo'),
    # path('templateone/render/<str:title>/', RenderTemplateView.as_view(), name='rendertemplateone'),
]