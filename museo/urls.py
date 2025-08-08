# museo/urls.py
from django.urls import path
from . import views

# Aggiungiamo un app_name per una migliore organizzazione
app_name = 'museo'

urlpatterns = [
    # Il percorso ora è '' perché il prefisso 'museo/' è già nel file urls.py principale
    # L'URL completo sarà /museo/temi/
    path('temi/', views.lista_temi, name='lista_temi'),
    path('sale/', views.lista_sale, name='lista_sale'),
    path('autori/', views.lista_autori, name='lista_autori'),
    path('opere/', views.lista_opere, name='lista_opere'),

    # URL per il CRUD delle Opere
    path('opere/nuova/', views.opera_gestisci, name='opera_nuova'),
    path('opere/<int:pk>/modifica/', views.opera_gestisci, name='opera_modifica'),
    path('opere/<int:pk>/elimina/', views.opera_elimina, name='opera_elimina'),

    path('ajax/nuovo_autore/', views.nuovo_autore_ajax, name='nuovo_autore_ajax'),
]