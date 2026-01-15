export const status = {
    pendente: "pendente",
    pago: "pago",
    reprovado: "reprovado",
}

export const statusLabel = {
    pendente: "Pendente",
    pago: "Pago",
    reprovado: "Reprovado",
}

export const traduzirStatus = function(status) {
    return statusLabel[status];
}