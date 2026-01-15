export function isValidCPF(cpf) {
    // Remove all non-numeric characters
    cpf = cpf.replace(/[^\d]/g, '');
    
    // Check if it has 11 digits
    if (cpf.length !== 11) {
        return false;
    }

    // Check if all digits are the same
    if (/^(\d)\1+$/.test(cpf)) {
        return false;
    }

    // Validate first digit
    let sum = 0;
    for (let i = 0; i < 9; i++) {
        sum += parseInt(cpf.charAt(i)) * (10 - i);
    }
    let remainder = 11 - (sum % 11);
    const digit1 = remainder >= 10 ? 0 : remainder;

    if (digit1 !== parseInt(cpf.charAt(9))) {
        return false;
    }

    // Validate second digit
    sum = 0;
    for (let i = 0; i < 10; i++) {
        sum += parseInt(cpf.charAt(i)) * (11 - i);
    }
    remainder = 11 - (sum % 11);
    const digit2 = remainder >= 10 ? 0 : remainder;

    return digit2 === parseInt(cpf.charAt(10));
}

export function isValidCNPJ(cnpj) {
    // Remove all non-numeric characters
    cnpj = cnpj.replace(/[^\d]/g, '');
    
    // Check if it has 14 digits
    if (cnpj.length !== 14) {
        return false;
    }

    // Check if all digits are the same
    if (/^(\d)\1+$/.test(cnpj)) {
        return false;
    }

    // Validate first digit
    let length = cnpj.length - 2;
    let numbers = cnpj.substring(0, length);
    const digits = cnpj.substring(length);
    let sum = 0;
    let pos = length - 7;
    
    for (let i = length; i >= 1; i--) {
        sum += parseInt(numbers.charAt(length - i)) * pos--;
        if (pos < 2) {
            pos = 9;
        }
    }
    
    let result = sum % 11 < 2 ? 0 : 11 - (sum % 11);
    if (result !== parseInt(digits.charAt(0))) {
        return false;
    }

    // Validate second digit
    length = length + 1;
    numbers = cnpj.substring(0, length);
    sum = 0;
    pos = length - 7;
    
    for (let i = length; i >= 1; i--) {
        sum += parseInt(numbers.charAt(length - i)) * pos--;
        if (pos < 2) {
            pos = 9;
        }
    }
    
    result = sum % 11 < 2 ? 0 : 11 - (sum % 11);
    return result === parseInt(digits.charAt(1));
}

export function isValidCPFOrCNPJ(value) {
    // Remove all non-numeric characters
    const cleanValue = value.replace(/[^\d]/g, '');
    
    // Check length to determine if it's CPF or CNPJ
    if (cleanValue.length === 11) {
        return isValidCPF(cleanValue);
    } else if (cleanValue.length === 14) {
        return isValidCNPJ(cleanValue);
    }
    
    return false;
}

export function formatCPF(cpf) {
    // Remove all non-numeric characters
    const cleaned = cpf.replace(/\D/g, '');
    
    // Format CPF progressively as user types
    if (cleaned.length <= 3) {
        return cleaned;
    } else if (cleaned.length <= 6) {
        return cleaned.replace(/(\d{3})(\d{1,3})/, "$1.$2");
    } else if (cleaned.length <= 9) {
        return cleaned.replace(/(\d{3})(\d{3})(\d{1,3})/, "$1.$2.$3");
    } else {
        return cleaned.replace(/(\d{3})(\d{3})(\d{3})(\d{1,2})/, "$1.$2.$3-$4");
    }
}

export function formatCNPJ(cnpj) {
    // Format CNPJ as 00.000.000/0000-00
    return cnpj.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5");
}
