# museo/management/commands/importa_dati.py

import csv
from django.core.management.base import BaseCommand
from museo.models import Autore, Tema, Sala, Opera

class Command(BaseCommand):
    help = 'Importa i dati del museo dai file CSV'

    def handle(self, *args, **kwargs):
        self.stdout.write("Cancellazione dei vecchi dati...")
        Opera.objects.all().delete()
        Sala.objects.all().delete()
        Tema.objects.all().delete()
        Autore.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Dati esistenti cancellati."))

        try:
            # 1. Importa Temi
            # Assumiamo che anche gli altri file usino il punto e virgola
            with open('Tema.csv', mode='r', encoding='utf-8') as file:
                # MODIFICA: Specificato il punto e virgola come separatore
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    Tema.objects.create(
                        codice=row['codice'],
                        descrizione=row['descrizione']
                    )
            self.stdout.write(self.style.SUCCESS('Temi importati con successo.'))

            # 2. Importa Autori
            with open('Autore.csv', mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    data_nascita = row['dataNascita'] if row.get('dataNascita') and row['dataNascita'] != 'NULL' else None
                    data_morte = row['dataMorte'] if row.get('dataMorte') and row['dataMorte'] != 'NULL' else None
                    
                    Autore.objects.create(
                        codice=row['codice'],
                        nome=row['nome'],
                        cognome=row['cognome'],
                        dataNascita=data_nascita,
                        dataMorte=data_morte,
                        nazionalita=row['nazione'],
                        # --- MODIFICA CHIAVE: Leggiamo la colonna 'tipo' e la salviamo nel campo 'stato' ---
                        stato=row['tipo']
                    )
            self.stdout.write(self.style.SUCCESS('Autori importati con successo.'))

            # 3. Importa Sale
            with open('Sala.csv', mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    tema_obj = None
                    if row.get('codTema') and row['codTema'] != 'NULL':
                        try:
                            tema_obj = Tema.objects.get(codice=row['codTema'])
                        except Tema.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f"Tema con codice {row['codTema']} non trovato. La sala {row['numero']} avrà tema nullo."))
                    
                    Sala.objects.create(
                        numero=row['numero'],
                        nome=row['nome'],
                        superficie=row['superficie'],
                        tema=tema_obj
                    )
            self.stdout.write(self.style.SUCCESS('Sale importate con successo.'))
            
            # 4. Importa Opere
            with open('Opera.csv', mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    autore_obj = None
                    # --- CORREZIONE QUI ---
                    # Cerca la colonna 'codAutore' invece di 'autore'
                    if row.get('codAutore') and row['codAutore'] != 'NULL':
                        try:
                            autore_obj = Autore.objects.get(codice=row['codAutore'])
                        except Autore.DoesNotExist:
                             self.stdout.write(self.style.WARNING(f"Autore con codice {row['codAutore']} non trovato."))

                    sala_obj = None
                    if row.get('espostaInSala') and row['espostaInSala'] != 'NULL':
                        try:
                            sala_obj = Sala.objects.get(numero=row['espostaInSala'])
                        except Sala.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f"Sala con numero {row['espostaInSala']} non trovata."))

                    Opera.objects.create(
                        codice=row['codice'],
                        titolo=row['titolo'],
                        annoRealizzazione=row['annoRealizzazione'] if row.get('annoRealizzazione') else None,
                        annoAcquisto=row['annoAcquisto'] if row.get('annoAcquisto') else None,
                        tipo=row['tipo'],
                        autore=autore_obj,
                        espostaInSala=sala_obj
                    )
            self.stdout.write(self.style.SUCCESS('Opere importate con successo.'))

        except FileNotFoundError as e:
            self.stdout.write(self.style.ERROR(f"Errore: File non trovato. Assicurati che il file '{e.filename}' sia nella cartella principale del progetto."))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Si è verificato un errore durante l'importazione: {e}"))
            return

        self.stdout.write(self.style.SUCCESS('Tutti i dati sono stati importati correttamente!'))