import { useState, useEffect } from 'react';

const Capsula = function({ label, children, light }) {
    if(label) {
        return (<label>
            <div className={light ? "mb-1 text-white" : "mb-1 text-black"}>{label}</div>
            {children}
        </label>)
    } else {
        return children;
    }
}

const CpfCnpjInput = function ({ label, name, placeholder, required, value, onChange, light, disabled, ...rest }) {
    const [displayValue, setDisplayValue] = useState('');

    // Formata o valor para exibição
    const formatValue = (rawValue) => {
        const clean = rawValue.replace(/\D/g, '');

        if (clean.length <= 11) {
            // Formata como CPF
            return clean
                .replace(/(\d{3})(\d)/, '$1.$2')
                .replace(/(\d{3})(\d)/, '$1.$2')
                .replace(/(\d{3})(\d{1,2})$/, '$1-$2');
        } else {
            // Formata como CNPJ
            return clean
                .slice(0, 14) // Limita a 14 dígitos para CNPJ
                .replace(/(\d{2})(\d)/, '$1.$2')
                .replace(/(\d{3})(\d)/, '$1.$2')
                .replace(/(\d{3})(\d)/, '$1/$2')
                .replace(/(\d{4})(\d{1,2})$/, '$1-$2');
        }
    };

    // Inicializa com o valor prop
    useEffect(() => {
        if (value !== undefined && value !== null) {
            setDisplayValue(formatValue(value.toString()));
        } else {
            setDisplayValue('');
        }
    }, [value]);

    const handleChange = (e) => {
        const rawValue = e.target.value;
        const cleanValue = rawValue.replace(/\D/g, '');

        // Formata para exibição
        const formatted = formatValue(cleanValue);
        setDisplayValue(formatted);

        // Dispara o evento com apenas números
        const syntheticEvent = {
            ...e,
            target: {
                ...e.target,
                value: cleanValue,
                name: name
            }
        };

        onChange(syntheticEvent);
    };

    const handleKeyDown = (e) => {
        // Permite apenas teclas numéricas e de controle
        if (!/[0-9]|Backspace|Delete|ArrowLeft|ArrowRight|Tab/.test(e.key)) {
            e.preventDefault();
        }
    };

    return (
        <div>
            <Capsula label={label} light={light}>
                <input
                    required={required}
                    type="text"
                    name={name}
                    placeholder={placeholder}
                    value={displayValue}
                    onChange={handleChange}
                    onKeyDown={handleKeyDown}
                    disabled={disabled}
                    {...rest}
                    className={"w-full h-14 rounded-2xl px-4 outline-0 bg-foreground text-white text-sm disabled:opacity-70 " + (rest?.className ?? "")}
                />
            </Capsula>
        </div>
    );
};

export default CpfCnpjInput;