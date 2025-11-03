document.addEventListener('DOMContentLoaded', function() {
    const respostaInput = document.getElementById('resposta');
    const enviarBtn = document.getElementById('enviar-resposta');
    const feedbackDiv = document.getElementById('feedback');
    
    if (enviarBtn) {
        enviarBtn.addEventListener('click', enviarResposta);
        respostaInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                enviarResposta();
            }
        });
    }
    
    function enviarResposta() {
        const resposta = respostaInput.value.trim();
        
        if (!resposta) {
            mostrarFeedback('Por favor, digite uma resposta.', false);
            return;
        }
        
        fetch('/check_answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({resposta: resposta})
        })
        .then(response => response.json())
        .then(data => {
            if (data.correct) {
                playSound('correct');
                mostrarFeedback(data.message, true);
                
                if (gameMode === 'multiple') {
                    atualizarPalavrasEncontradas(data.found_words);
                    if (data.completed) {
                        finalizarJogo();
                    }
                } else if (gameMode === 'text') {
                    atualizarTextoRevelado(data.revealed_text);
                    if (data.completed) {
                        finalizarJogo();
                    }
                } else if (gameMode === 'single' && data.correct) {
                    finalizarJogo();
                }
                
                respostaInput.value = '';
            } else {
                playSound('wrong');
                mostrarFeedback(data.message, false);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            mostrarFeedback('Erro ao enviar resposta. Tente novamente.', false);
        });
    }
    
    function mostrarFeedback(mensagem, correto) {
        feedbackDiv.textContent = mensagem;
        feedbackDiv.className = 'feedback ' + (correto ? 'correct' : 'incorrect');
        
        // Auto-esconder após 3 segundos
        setTimeout(() => {
            feedbackDiv.style.display = 'none';
        }, 3000);
    }
    
    function playSound(type) {
        // Implementar toque de som (precisa dos arquivos de som)
        // const audio = new Audio(`/static/sounds/${type}.mp3`);
        // audio.play().catch(e => console.log('Erro ao reproduzir som:', e));
    }
    
    function atualizarPalavrasEncontradas(palavras) {
        const foundCount = document.getElementById('found-count');
        const foundWordsList = document.getElementById('found-words-list');
        
        if (foundCount) foundCount.textContent = palavras.length;
        
        if (foundWordsList) {
            foundWordsList.innerHTML = '';
            palavras.forEach(palavra => {
                const badge = document.createElement('span');
                badge.className = 'word-badge';
                badge.textContent = palavra;
                foundWordsList.appendChild(badge);
            });
        }
    }
    
    function atualizarTextoRevelado(texto) {
        const revealedText = document.getElementById('revealed-text');
        if (revealedText) revealedText.textContent = texto;
    }
    
    function finalizarJogo() {
        setTimeout(() => {
            if (confirm('Parabéns! Você completou o jogo! Deseja jogar novamente?')) {
                location.reload();
            }
        }, 1000);
    }
    
    // Inicialização para modo múltiplo
    if (gameMode === 'multiple' && totalWords) {
        document.getElementById('total-count').textContent = totalWords;
    }
});