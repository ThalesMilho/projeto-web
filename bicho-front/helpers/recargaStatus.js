export const status = {
    pendente: "pendente",
    pago: "pago",
    cancelado: "cancelado",
    devolvido: "devolvido",
}

export const statusLabel = {
    pendente: "Pendente",
    pago: "Pago",
    cancelado: "Cancelado",
    devolvido: "Devolvido",
}

export const traduzirStatus = function(status) {
    return statusLabel[status];
}