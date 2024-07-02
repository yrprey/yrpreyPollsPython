$(document).ready(function() {
    // Função para carregar enquetes
    function loadPolls() {
        $.ajax({
            url: 'http://localhost:3000/list_polls',
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                let pollList = '';
                data.forEach(poll => {
                    pollList += `<li class="list-group-item"><a href="poll.php?id=${poll.id}" style="color: #B71C1C;">${poll.question}</a></li>`;
                });
                $('#pollList').html(pollList);
                $('#managePollList').html(pollList);
            }
        });
    }

    // Carregar enquetes na inicialização
    loadPolls();

    // Login
    $('#loginForm').on('submit', function(e) {
        e.preventDefault();
        const username = $('#username').val();
        const password = $('#password').val();
        $.ajax({
            url: 'http://localhost:3000/login',
            method: 'POST',
            data: { username, password },
            success: function(response) {
                if (response.includes('success')) {
                    window.location.href = 'index.php';
                } else {    
                    $('#message').html('<div class="alert alert-danger" role="alert">Credentials invalid!</div>'+response);
                }
            }
        });
    });

    // Registro
    $('#registerForm').on('submit', function(e) {
        e.preventDefault(); 
        const username = $('#username').val();
        const password = $('#password').val();
        $.ajax({
            url: 'http://localhost:3000/register',
            method: 'POST',
            data: { username, password },
            success: function(response) {
                if (response.includes('success')) {
                    window.location.href = 'index.php';
                } else {
                    $('#message').html('<div class="alert alert-danger" role="alert">Error to register!</div>');
                }
            }
        });
    });

    // Criar Enquete
    $('#pollForm').on('submit', function(e) {
        e.preventDefault();
        const question = $('#question').val();
        const options = $('#options').val().split(','); // Assuming options are comma-separated
        const id = 1; // Replace with actual id value or dynamically set it
    
        $.ajax({
            url: 'http://localhost:3000/create_poll',
            method: 'POST',
            contentType: 'application/json', // Set the content type to JSON
            data: JSON.stringify({ question: question, options: options, id: id }), // Convert data to JSON
            success: function(response) {
                if (response.status === 'success') {
                    loadPolls();
                    $('#message').html('<br><div class="alert card green lighten-4 green-text text-darken-4"><div class="card-content"><p><i class="material-icons">check_circle</i><span>&nbsp;&nbsp;Success:</span> &nbsp;&nbsp; Enquete criada com sucesso!.</p></div></div>');
                } else {
                    $('#message').html('<div class="alert alert-success" role="alert">Falha ao criar enquete!</div>');
                }
            },
            error: function(xhr, status, error) {
                console.error('Erro:', error);
                $('#message').html('<div class="alert alert-danger" role="alert">Erro ao criar enquete!</div>');
            }
        });
    });
    

    // Carregar detalhes da enquete
    if (window.location.pathname.includes('poll.php')) {
        const pollId = new URLSearchParams(window.location.search).get('id');
        $.ajax({
            url: `http://localhost:3000/get_poll?id=${pollId}`,
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                let pollDetails = `<h4>${data.question}</h4>`;
                data.options.forEach(option => {
                    pollDetails += `
                        <div class="form-check">
                            <input class="form-check-input" type="radio" name="options" id="option${option.id}" value="${option.id}">
                            <label class="form-check-label" for="option${option.id}"style="font-size:32px;">
                                ${option.option_text}
                            </label>
                        </div>
                    `;
                });
                pollDetails += `<button class="btn btn-primary mt-3" id="voteButton" style="background-color:#B71C1C">Votar</button>`;
                $('#pollDetails').html(pollDetails);

                // Votação
                
                $('#voteButton').on('click', function() {
                    const optionId = $('input[name="options"]:checked').val();
                    $.ajax({
                        url: 'http://localhost:3000/vote',
                        method: 'POST',
                        contentType: 'application/json', // Set the content type to JSON
                        data: JSON.stringify({ poll_id: pollId, option_id: optionId, id: user_id }), // Convert data to JSON                        
                        success: function(response) {                            
                            if (response.status === 'success') {
                                //$('#message').html('<div class="alert alert-success" role="alert">Voto registrado com sucesso!</div>');
                                window.location.href = `results.php?id=${pollId}`;
                            } else {
                                $('#message').html('<div class="alert alert-danger" role="alert">Falha ao registrar voto!</div>');
                            }
                        }
                    });
                });
            }
        });
    }

    // Carregar resultados da enquete
    if (window.location.pathname.includes('results.php')) {
        const pollId = new URLSearchParams(window.location.search).get('id');
        $.ajax({
            url: `http://localhost:3000/get_results?id=${pollId}`,
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                let resultsDetails = `<h2>${data.question}</h2>`;
                data.results.forEach(result => {
                    resultsDetails += `
                        <p>${result.option_text}: ${result.votes} votos</p>
                    `;
                });
                $('#resultsDetails').html(resultsDetails);
            }
        });
    }
});
