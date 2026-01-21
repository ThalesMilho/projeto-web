export const calcularMultiplicador = function(vinculo, tipoProbabilidade='A') {
    let base = parseFloat(vinculo?.base);
    let prob = vinculo.probabilidadeA;
        if(tipoProbabilidade === "B")
            prob = parseInt(vinculo.probabilidadeB);

    let novaBase = ((base * 50) / prob);

    // let percentNovaBase = (novaBase * percent / 100);
    // return novaBase.toFixed(1);
    if(vinculo.forcaA !== null && vinculo.forcaA !== 0) {
        if(tipoProbabilidade === 'B') {
            novaBase += novaBase * (vinculo.forcaA / 70);
        } else if (tipoProbabilidade === 'A') {
            novaBase -= novaBase * (vinculo.forcaA / 70);
        }
    }

    if(vinculo?.min && novaBase < vinculo?.min)
        return parseFloat(vinculo?.min);
    if(vinculo?.max && novaBase > vinculo?.max)
        return parseFloat(vinculo?.max);

    return novaBase.toFixed(1);
}