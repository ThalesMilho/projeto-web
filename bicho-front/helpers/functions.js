import {getCookie, setCookie} from "cookies-next";

export const only_numbers = function(str) {
    return str.replace(/\D/g, "");
}

export const formatarCelular = function (phoneNumber) {
    if(!phoneNumber)
        return "";
    const number = phoneNumber.toString();

    const formatted = number.replace(
        /^(\d{2})(\d{1})(\d{4})(\d{4})$/,
        "($1) $2 $3-$4"
    );

    return formatted;
}

export const toMoney = function(str) {
    return parseFloat(str).toLocaleString('pt-br',{style: 'currency', currency: 'BRL'})
}

export const validarCPF = function(cpf) {
    // Remove caracteres não numéricos (como pontos e traços)
    cpf = cpf.replace(/\D/g, '');

    // Verifica se o CPF tem 11 dígitos ou se todos os dígitos são iguais
    if (cpf.length !== 11 || /^(\d)\1+$/.test(cpf)) {
        return false;
    }

    // Função para calcular o dígito verificador
    function calcularDigito(cpf, pesoInicial) {
        let soma = 0;
        for (let i = 0; i < pesoInicial - 1; i++) {
            soma += parseInt(cpf[i]) * (pesoInicial - i);
        }
        const resto = soma % 11;
        return resto < 2 ? 0 : 11 - resto;
    }

    // Calcula os dois dígitos verificadores
    const digito1 = calcularDigito(cpf, 10);
    const digito2 = calcularDigito(cpf, 11);

    // Verifica se os dígitos calculados coincidem com os fornecidos
    return digito1 === parseInt(cpf[9]) && digito2 === parseInt(cpf[10]);
}

export const formatarCPF = function(cpf) {
    // Remove quaisquer caracteres não numéricos
    cpf = cpf.replace(/\D/g, '');

    // Verifica se o CPF tem exatamente 11 dígitos
    if (cpf.length !== 11) {
        return null;
    }

    // Formata o CPF no formato XXX.XXX.XXX-XX
    return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
}

export const realToFloat = function(brlString) {
    // Remove os pontos usados como separadores de milhar
    brlString = brlString.toString();
    let cleanedString = brlString.replace(/\./g, '');

    // Substitui a vírgula decimal por um ponto
    cleanedString = cleanedString.replace(',', '.');

    // Converte para float
    const floatValue = parseFloat(cleanedString);

    // Retorna o valor numérico
    return floatValue;
}

export const getNomeUsuarioLogado = function() {
    return getCookie("usuarioNome") ?? '';
}

export const getIdUsuarioLogado = function() {
    return getCookie("usuarioId") ?? 'asdasdasdasdasdasdasd';
}

export const verificarUsuarioLogado = function() {
    return true; // SÓ TESTANDO, PODE EXPLODIR ISSO AQUI QUANDO QUISER
    return getCookie("usuarioNome") && getCookie("usuarioId");
}

export const somNotificacao = function() {
    try {
        // Método 1: Som gerado programaticamente (mais confiável)
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        // Configurações do som
        oscillator.frequency.setValueAtTime(800, audioContext.currentTime); // Frequência
        oscillator.type = 'sine'; // Tipo de onda

        // Volume
        gainNode.gain.setValueAtTime(0, audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.1, audioContext.currentTime + 0.01);
        gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.3);

        // Duração do som
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.3);

    } catch (error) {
        // Fallback: Som mais simples usando Data URL
        try {
            const audio = new Audio();
            // Som de beep simples em base64
            audio.src = "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmEaAjSMzO3QfzoFJHfH8N2QQAoUXrTp66hVFApGn+DyvmEaAjSMzO3QfzoFI3bD7d2MQAkVYrvs55lLEg0";
            audio.volume = 0.3;
            audio.play();
        } catch (fallbackError) {
            console.log('Não foi possível reproduzir som de notificação');
        }
    }
};