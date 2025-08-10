$(document).ready(function() {

    var djangoMessageBox = $('#django-message-data');
    if (djangoMessageBox.length) {
        var messageText = djangoMessageBox.data('message');
        if (messageText) {
            $('#message-text').text(messageText);
            $('#message-overlay').removeClass('hidden');
        }
    }

    // Gestione "Nuovo Autore"

    $('#btn-nuovo-autore').on('click', function() {
        // Pulisce eventuali errori precedenti prima di aprire
        $('#form-nuovo-autore .error-message').text('');
        $('#modal-autore').removeClass('hidden');
    });

    $('#btn-chiudi-modal').on('click', function() {
        $('#modal-autore').addClass('hidden');
    });

    $(document).on('keydown', function(event) {
        if (event.key === "Escape") {
            $('.modal-overlay').addClass('hidden');
        }
    });

    // Mostra/nasconde il campo data di morte in base allo stato "vivo/morto"
    $('#nuovo_stato').on('change', function() {
        if ($(this).val() === 'morto') {
            $('#campo-data-morte').removeClass('hidden');
        } else {
            $('#campo-data-morte').addClass('hidden');
            $('#nuova_dataMorte').val('');
        }
    });

    // --- Validazione in tempo reale per il form del NUOVO AUTORE ---
    function validaFormAutore() {
        $('#form-nuovo-autore .error-message').text('');
        var nome = $('#nuovo_nome').val().trim();
        var cognome = $('#nuovo_cognome').val().trim();
        var dataNascita = $('#nuova_dataNascita').val();
        var dataMorte = $('#nuova_dataMorte').val();
        var stato = $('#nuovo_stato').val();
        var dataCorrente = new Date().toISOString().split('T')[0];
        var isFormValido = true;

        if (nome === '') {
            $('#errore-nome-autore').text('Il nome è obbligatorio.');
            isFormValido = false;
        }
        if (cognome === '') {
            $('#errore-cognome-autore').text('Il cognome è obbligatorio.');
            isFormValido = false;
        }
        if (dataNascita && dataNascita > dataCorrente) {
            $('#errore-data-nascita').text('La data di nascita non può essere nel futuro.');
            isFormValido = false;
        }
        if (dataMorte && dataMorte > dataCorrente) {
            $('#errore-data-morte').text('La data di morte non può essere nel futuro.');
            isFormValido = false;
        }
        if (dataNascita && dataMorte) {
            var nascita = new Date(dataNascita);
            var morte = new Date(dataMorte);
            if (morte < nascita) {
                $('#errore-data-morte').text('La data di morte non può precedere la nascita.');
                isFormValido = false;
            }
            var differenzaAnni = (morte.getTime() - nascita.getTime()) / (1000 * 3600 * 24 * 365.25);
            if (differenzaAnni > 100) {
                $('#errore-data-morte').text('L\'autore non può vivere più di 100 anni.');
                isFormValido = false;
            }
        }
        if (stato === 'vivo' && dataNascita) {
            var nascita = new Date(dataNascita);
            var oggi = new Date();
            var eta = (oggi.getTime() - nascita.getTime()) / (1000 * 3600 * 24 * 365.25);
            if (eta > 100) {
                $('#errore-data-nascita').text('Un autore vivente non può avere più di 100 anni.');
                isFormValido = false;
            }
        }
        if (stato === 'morto' && dataMorte === '') {
            $('#errore-data-morte').text('La data di morte è obbligatoria per un autore deceduto.');
            isFormValido = false;
        }
        return isFormValido;
    }

    $('#nuova_dataNascita, #nuova_dataMorte').on('change keyup', validaFormAutore);

    // --- Chiamata AJAX per salvare il nuovo autore ---
    $('#form-nuovo-autore').on('submit', function(e) {
        e.preventDefault();
        if (!validaFormAutore()) {
            return;
        }

        var ajaxUrl = $(this).data('url');
        var formData = $(this).serialize();

        $.ajax({
            type: 'POST',
            url: ajaxUrl,
            data: formData,
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    var nuovoAutore = response.nuovo_autore;
                    var nuovaOpzione = $('<option>', { value: nuovoAutore.id, text: nuovoAutore.nome_completo });
                    nuovaOpzione.attr('data-nascita', nuovoAutore.dataNascita);
                    nuovaOpzione.attr('data-morte', nuovoAutore.dataMorte);

                    $('#id_autore').append(nuovaOpzione);
                    $('#id_autore').val(nuovoAutore.id).trigger('change');
                    $('#modal-autore').addClass('hidden');
                    $('#form-nuovo-autore')[0].reset();
                    
                    $('#message-text').text(`Autore "${nuovoAutore.nome_completo}" aggiunto con successo!`);
                    $('#message-overlay').removeClass('hidden');
                } else {
                    var error_messages = JSON.parse(response.errors);
                    var alert_text = "Errore di validazione:\n";
                    for (var field in error_messages) {
                        alert_text += `- ${error_messages[field][0].message}\n`;
                    }
                    alert(alert_text);
                }
            },
            error: function() {
                alert('Si è verificato un errore di comunicazione con il server.');
            }
        });
    });


    // Gestione form Opera
    // Validazione per gli anni
    function validaAnniOpera() {
        var opzioneAutore = $('#id_autore option:selected');
        var annoRealizzazioneInput = $('#id_annoRealizzazione');
        var annoAcquistoInput = $('#id_annoAcquisto');
        var erroreAutoreDiv = $('#errore-anno-autore');
        var erroreAcquistoDiv = $('#errore-anno-acquisto');

        var annoRealizzazione = parseInt(annoRealizzazioneInput.val());
        var annoAcquisto = parseInt(annoAcquistoInput.val());
        var dataNascitaAttr = opzioneAutore.data('nascita');
        var dataMorteAttr = opzioneAutore.data('morte');
        var annoCorrente = new Date().getFullYear();

        erroreAutoreDiv.text('');
        erroreAcquistoDiv.text('');

        if (annoRealizzazione) {
            if (annoRealizzazione > annoCorrente) {
                erroreAutoreDiv.text('L\'anno di realizzazione non può essere nel futuro.');
            } else if (dataNascitaAttr) {
                var annoNascita = parseInt(String(dataNascitaAttr).substring(0, 4));
                var annoMorte = dataMorteAttr ? parseInt(String(dataMorteAttr).substring(0, 4)) : null;

                if (annoRealizzazione < annoNascita) {
                    erroreAutoreDiv.text('L\'anno non può precedere la nascita dell\'autore (' + annoNascita + ').');
                } else if (annoMorte && annoRealizzazione > annoMorte) {
                    erroreAutoreDiv.text('L\'anno non può essere successivo alla morte dell\'autore (' + annoMorte + ').');
                }
            }
        }
        if (annoAcquisto) {
            if (annoAcquisto > annoCorrente) {
                erroreAcquistoDiv.text('L\'anno di acquisto non può essere nel futuro.');
            } else if (annoRealizzazione && annoAcquisto < annoRealizzazione) {
                erroreAcquistoDiv.text('L\'anno di acquisto non può precedere quello di realizzazione.');
            }
        }
    }

    $('#id_autore, #id_annoRealizzazione, #id_annoAcquisto').on('change keyup', validaAnniOpera);


    // Gestione Conferme

    // Conferma eliminazione
    $('.btn-delete-confirm').on('click', function(e) {
        e.preventDefault();
        var urlElimina = $(this).data('url');
        var titoloOpera = $(this).data('titolo');
        $('#conferma-testo').html("Sei sicuro di voler eliminare l'opera: <br><strong>" + titoloOpera + "</strong>?<br>L'azione è irreversibile.");
        $('#modal-conferma-elimina').find('form').attr('action', urlElimina);
        $('#modal-conferma-elimina').removeClass('hidden');
    });

    $('#btn-annulla-elimina').on('click', function() {
        $('#modal-conferma-elimina').addClass('hidden');
    });

    $('#message-close-btn').on('click', function() {
        $('#message-overlay').addClass('hidden');
    });

});