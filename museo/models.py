from django.db import models

class Autore(models.Model):
    codice = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    dataNascita = models.DateField(null=True, blank=True)
    dataMorte = models.DateField(null=True, blank=True)
    nazionalita = models.CharField(max_length=50, blank=True)

    STATO_CHOICES = [
        ('vivo', 'Vivo'),
        ('morto', 'Morto'),
    ]
    stato = models.CharField(
        max_length=5,
        choices=STATO_CHOICES,
        default='vivo',
        help_text="Stato dell'artista"
    )

    class Meta:
        verbose_name = "Autore"
        verbose_name_plural = "Autori"
        ordering = ['cognome', 'nome']

    def __str__(self):
        return f"{self.nome} {self.cognome}"


class Tema(models.Model):
    codice = models.AutoField(primary_key=True)
    descrizione = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Tema"
        verbose_name_plural = "Temi"
        ordering = ['descrizione']

    def __str__(self):
        return self.descrizione


class Sala(models.Model):
    # Qui 'numero' non è la chiave primaria, quindi lo definiamo come campo normale.
    # L'ID automatico di Django sarà la vera chiave primaria.
    numero = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=100)
    superficie = models.DecimalField(
        max_digits=7, 
        decimal_places=2, 
        help_text="Superficie in metri quadrati"
    )
    
    # Relazione con Tema
    tema = models.ForeignKey(
        Tema, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Tema della sala"
    )

    class Meta:
        verbose_name = "Sala"
        verbose_name_plural = "Sale"
        ordering = ['numero']

    def __str__(self):
        return f"Sala {self.numero}: {self.nome}"


class Opera(models.Model):
    codice = models.AutoField(primary_key=True)
    titolo = models.CharField(max_length=200)
    annoRealizzazione = models.IntegerField(null=True, blank=True)
    annoAcquisto=models.IntegerField(null=True, blank=True)
    
    # Il campo 'tipo' che era una stringa (Quadro/Scultura)
    TIPO_CHOICES = [
        ('Quadro', 'Quadro'),
        ('Scultura', 'Scultura'),
        ('Non specificato', 'Non specificato'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='Non specificato')
    
    # Relazioni con Autore e Sala
    autore = models.ForeignKey(
        Autore, 
        on_delete=models.CASCADE, 
        verbose_name="Autore dell'opera"
    )
    espostaInSala = models.ForeignKey(
        Sala, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Sala di esposizione"
    )

    class Meta:
        verbose_name = "Opera"
        verbose_name_plural = "Opere"
        ordering = ['titolo']

    def __str__(self):
        return self.titolo