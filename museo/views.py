from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count
from django.core.paginator import Paginator
from .models import Tema, Sala, Autore, Opera
from .forms import OperaForm, AutoreForm


def index(request):
    """
    Questa vista gestisce la homepage.
    """
    return render(request, 'museo/index.html')


def lista_temi(request):
    """
    Questa vista gestisce la ricerca, l'ordinamento e la paginazione dei Temi.
    """
    queryset = Tema.objects.annotate(numero_sale=Count('sala')).all()

    search_descrizione = request.GET.get('descrizione', '')
    if search_descrizione:
        queryset = queryset.filter(descrizione__icontains=search_descrizione)

    colonne_ordinabili = ['descrizione', 'numero_sale']
    ordina_per = request.GET.get('ordina_per', 'descrizione')
    direzione = request.GET.get('direzione', 'asc')

    if ordina_per in colonne_ordinabili:
        if direzione == 'desc':
            queryset = queryset.order_by(f'-{ordina_per}')
        else:
            queryset = queryset.order_by(ordina_per)

    paginator = Paginator(queryset, 10)
    pagina_corrente = request.GET.get('pagina', 1)
    page_obj = paginator.get_page(pagina_corrente)

    context = {
        'page_obj': page_obj,
        'ordina_per': ordina_per,
        'direzione': direzione,
        'search_descrizione': search_descrizione
    }
    return render(request, 'museo/lista_temi.html', context)

def lista_sale(request):
    """
    Gestisce la ricerca, ordinamento e paginazione delle Sale.
    """
    queryset = Sala.objects.select_related('tema').annotate(numero_opere=Count('opera'))
    search_numero = request.GET.get('numero', '')
    search_nome = request.GET.get('nome', '')
    search_tema = request.GET.get('tema', '')

    if search_numero:
        queryset = queryset.filter(numero=search_numero)
    if search_nome:
        queryset = queryset.filter(nome__icontains=search_nome)
    if search_tema:
        if search_tema == 'senza_tema':
            queryset = queryset.filter(tema__isnull=True)
        else:
            queryset = queryset.filter(tema__codice=search_tema)

    campi_ordinamento = {
        'numero': 'numero', 'nome': 'nome', 'superficie': 'superficie',
        'tema_descrizione': 'tema__descrizione', 'numero_opere': 'numero_opere'
    }
    ordina_per = request.GET.get('ordina_per', 'numero')
    direzione = request.GET.get('direzione', 'asc')
    campo_da_ordinare = campi_ordinamento.get(ordina_per, 'numero')

    if direzione == 'desc':
        queryset = queryset.order_by(f'-{campo_da_ordinare}')
    else:
        queryset = queryset.order_by(campo_da_ordinare)

    paginator = Paginator(queryset, 10)
    pagina_corrente = request.GET.get('pagina', 1)
    page_obj = paginator.get_page(pagina_corrente)
    temi_per_filtro = Tema.objects.all().order_by('descrizione')

    context = {
        'page_obj': page_obj, 'ordina_per': ordina_per, 'direzione': direzione,
        'search_numero': search_numero, 'search_nome': search_nome,
        'search_tema': search_tema, 'temi_per_filtro': temi_per_filtro
    }
    return render(request, 'museo/lista_sale.html', context)

def lista_autori(request):
    """
    Gestisce la ricerca, ordinamento e paginazione degli Autori.
    """
    queryset = Autore.objects.annotate(numero_opere=Count('opera'))
    search_nome = request.GET.get('nome', '')
    search_cognome = request.GET.get('cognome', '')
    search_nazione = request.GET.get('nazionalita', '')
    search_stato = request.GET.get('stato', '')

    if search_nome:
        queryset = queryset.filter(nome__icontains=search_nome)
    if search_cognome:
        queryset = queryset.filter(cognome__icontains=search_cognome)
    if search_nazione:
        queryset = queryset.filter(nazionalita__icontains=search_nazione)
    if search_stato:
        queryset = queryset.filter(stato=search_stato)

    ordina_per = request.GET.get('ordina_per', 'cognome')
    direzione = request.GET.get('direzione', 'asc')
    campi_ordinabili_validi = ['nome', 'cognome', 'nazionalita', 'dataNascita', 'dataMorte', 'numero_opere', 'stato']
    if ordina_per in campi_ordinabili_validi:
        if direzione == 'desc':
            queryset = queryset.order_by(f'-{ordina_per}')
        else:
            queryset = queryset.order_by(ordina_per)

    paginator = Paginator(queryset, 10)
    pagina_corrente = request.GET.get('pagina', 1)
    page_obj = paginator.get_page(pagina_corrente)

    context = {
        'page_obj': page_obj, 'ordina_per': ordina_per, 'direzione': direzione,
        'search_nome': search_nome, 'search_cognome': search_cognome,
        'search_nazione': search_nazione, 'search_stato': search_stato,
    }
    return render(request, 'museo/lista_autori.html', context)

def lista_opere(request):
    """
    Gestisce la ricerca, ordinamento e paginazione delle Opere.
    """
    queryset = Opera.objects.select_related('autore', 'espostaInSala').all()
    search_titolo = request.GET.get('titolo', '')
    search_anno = request.GET.get('anno', '')
    search_autore_nome = request.GET.get('autore_nome', '')
    search_autore_cognome = request.GET.get('autore_cognome', '')
    search_tipo = request.GET.get('tipo', '')
    search_sala = request.GET.get('sala', '')

    if search_titolo:
        queryset = queryset.filter(titolo__icontains=search_titolo)
    if search_anno:
        queryset = queryset.filter(annoRealizzazione=search_anno)
    if search_autore_nome:
        queryset = queryset.filter(autore__nome__icontains=search_autore_nome)
    if search_autore_cognome:
        queryset = queryset.filter(autore__cognome__icontains=search_autore_cognome)
    if search_tipo:
        queryset = queryset.filter(tipo=search_tipo)
    if search_sala:
        if search_sala == 'magazzino':
            queryset = queryset.filter(espostaInSala__isnull=True)
        else:
            queryset = queryset.filter(espostaInSala__numero=search_sala)

    campi_ordinamento = {
        'titolo': 'titolo', 'annoRealizzazione': 'annoRealizzazione',
        'cognome_autore': 'autore__cognome', 'nome_sala': 'espostaInSala__nome',
        'tipo': 'tipo',
    }
    ordina_per = request.GET.get('ordina_per', 'titolo')
    direzione = request.GET.get('direzione', 'asc')
    campo_da_ordinare = campi_ordinamento.get(ordina_per)

    if campo_da_ordinare:
        if direzione == 'desc':
            campo_da_ordinare = f'-{campo_da_ordinare}'
        if ordina_per == 'cognome_autore':
            campo_nome = '-autore__nome' if direzione == 'desc' else 'autore__nome'
            queryset = queryset.order_by(campo_da_ordinare, campo_nome)
        else:
            queryset = queryset.order_by(campo_da_ordinare)

    paginator = Paginator(queryset, 10)
    pagina_corrente = request.GET.get('pagina', 1)
    page_obj = paginator.get_page(pagina_corrente)
    sale_per_filtro = Sala.objects.all().order_by('nome')

    context = {
        'page_obj': page_obj, 'ordina_per': ordina_per, 'direzione': direzione,
        'search_titolo': search_titolo, 'search_anno': search_anno,
        'search_autore_nome': search_autore_nome, 'search_autore_cognome': search_autore_cognome,
        'search_tipo': search_tipo, 'search_sala': search_sala,
        'sale_per_filtro': sale_per_filtro,
    }
    return render(request, 'museo/lista_opere.html', context)

# Viste per il CRUD delle Opere

def opera_gestisci(request, pk=None):
    if pk:
        opera = get_object_or_404(Opera, pk=pk)
        page_title = "Modifica Opera"
        success_message = "Opera modificata con successo!"
    else:
        opera = None
        page_title = "Nuova Opera"
        success_message = "Opera creata con successo!"

    if request.method == 'POST':
        form = OperaForm(request.POST, instance=opera)
        if form.is_valid():
            form.save()
            messages.success(request, success_message)
            return redirect('museo:lista_opere')
    else:
        form = OperaForm(instance=opera)

    context = {
        'form': form,
        'page_title': page_title
    }
    return render(request, 'museo/opera_form.html', context)

def opera_elimina(request, pk):
    opera = get_object_or_404(Opera, pk=pk)
    if request.method == 'POST':
        titolo_opera = opera.titolo
        opera.delete()
        messages.success(request, f"L'opera '{titolo_opera}' è stata eliminata.")
        return redirect('museo:lista_opere')
    
    return render(request, 'museo/opera_confirm_delete.html', {'opera': opera})

def nuovo_autore_ajax(request):
    if request.method == 'POST':
        form = AutoreForm(request.POST)
        if form.is_valid():
            nuovo_autore = form.save()
            
            # Prepara la risposta JSON in caso di successo
            response_data = {
                'success': True,
                'nuovo_autore': {
                    'id': nuovo_autore.codice,
                    'nome_completo': f"{nuovo_autore.cognome} {nuovo_autore.nome}",
                    'dataNascita': nuovo_autore.dataNascita,
                    'dataMorte': nuovo_autore.dataMorte,
                }
            }
            return JsonResponse(response_data)
        else:
            # Prepara la risposta JSON in caso di errore di validazione
            response_data = {
                'success': False,
                'message': 'Errore di validazione',
                'errors': form.errors.as_json() # Invia gli errori dettagliati
            }
            return JsonResponse(response_data, status=400)
    
    # Risponde con un errore se non è una richiesta POST
    return JsonResponse({'success': False, 'message': 'Metodo non valido.'}, status=405)