# museo/forms.py
from django import forms
from .models import Opera, Autore
import datetime

class OperaForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rimuoviamo programmaticamente la scelta 'Non specificato' dal form
        # Lasciandola però disponibile nel modello per la ricerca
        nuove_scelte_tipo = [scelta for scelta in self.fields['tipo'].choices if scelta[0] != 'Non specificato']
        self.fields['tipo'].choices = nuove_scelte_tipo

    class Meta:
        model = Opera
        fields = ['titolo', 'annoRealizzazione', 'annoAcquisto', 'tipo', 'autore', 'espostaInSala']
        widgets = {
            'titolo': forms.TextInput(attrs={'required': True}),
            'tipo': forms.Select(attrs={'required': True}),
            'autore': forms.Select(attrs={'required': True}),
        }
        labels = {
            'annoRealizzazione': "Anno di Realizzazione",
            'annoAcquisto': "Anno di Acquisto",
            'autore': "Autore", # Modificato da codAutore per coerenza
            'espostaInSala': "Sala Espositiva",
        }

    def clean(self):
        # ... (la funzione clean rimane identica a prima)
        cleaned_data = super().clean()
        anno_realizzazione = cleaned_data.get("annoRealizzazione")
        anno_acquisto = cleaned_data.get("annoAcquisto")
        autore = cleaned_data.get("autore")
        anno_corrente = datetime.date.today().year

        if anno_realizzazione and anno_realizzazione > anno_corrente:
            self.add_error('annoRealizzazione', "L'anno di realizzazione non può essere nel futuro.")

        if anno_acquisto and anno_acquisto > anno_corrente:
            self.add_error('annoAcquisto', "L'anno di acquisto non può essere nel futuro.")

        if anno_acquisto and anno_realizzazione and anno_acquisto < anno_realizzazione:
            self.add_error('annoAcquisto', "L'anno di acquisto non può precedere quello di realizzazione.")

        if anno_realizzazione and autore:
            if autore.dataNascita and anno_realizzazione < autore.dataNascita.year:
                self.add_error('annoRealizzazione', f"L'anno di realizzazione non può precedere la nascita dell'autore ({autore.dataNascita.year}).")
            if autore.dataMorte and anno_realizzazione > autore.dataMorte.year:
                self.add_error('annoRealizzazione', f"L'anno di realizzazione non può essere successivo alla morte dell'autore ({autore.dataMorte.year}).")

        return cleaned_data
    
class AutoreForm(forms.ModelForm):
    class Meta:
        model = Autore
        fields = ['nome', 'cognome', 'nazionalita', 'dataNascita', 'stato', 'dataMorte']

    def clean(self):
        cleaned_data = super().clean()
        data_nascita = cleaned_data.get("dataNascita")
        data_morte = cleaned_data.get("dataMorte")
        stato = cleaned_data.get("stato")
        oggi = datetime.date.today()

        # Controllo #1: Le date non possono essere nel futuro
        if data_nascita and data_nascita > oggi:
            raise forms.ValidationError("La data di nascita non può essere nel futuro.")
        
        if data_morte and data_morte > oggi:
            raise forms.ValidationError("La data di morte non può essere nel futuro.")

        # Controllo #2: Morte non può precedere Nascita
        if data_nascita and data_morte and data_morte < data_nascita:
            raise forms.ValidationError("La data di morte non può precedere la data di nascita.")
        
        # Controllo #3: Morte non può distare più di 100 anni dalla nascita
        if data_nascita and data_morte:
            delta_anni = (data_morte - data_nascita).days / 365.25
            if delta_anni > 100:
                raise forms.ValidationError("Un autore non può vivere più di 100 anni.")

        if stato == 'vivo' and data_nascita:
            eta = (oggi - data_nascita).days / 365.25
            if eta > 100:
                raise forms.ValidationError("Un autore vivente non può avere più di 100 anni.")

        # Controlli di coerenza sullo stato
        if stato == 'morto' and not data_morte:
            raise forms.ValidationError("La data di morte è obbligatoria per un autore deceduto.")
            
        if stato == 'vivo':
            cleaned_data['dataMorte'] = None # Pulisce la data di morte se si imposta "Vivo"

        return cleaned_data