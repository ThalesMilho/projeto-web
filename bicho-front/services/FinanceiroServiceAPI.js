import ServiceAPI from './ServiceBaseAPI.js';

export default class FinanceiroServiceAPI extends ServiceAPI {

    async realizarRecarga(valor, documento) {
        try {
            return await this.http().post('recarga', {
                valor,
                documento
            });
        } catch (error) {
            return error.response;
        }
    }

    async realizarSaque(valor) {
        try {
            return await this.http().post('saque', {
                valor
            });
        } catch (error) {
            return error.response;
        }
    }

    async buscarHistoricoRecarga(page=1) {
        try {
            return await this.http().get(`recarga/historico?page=${page}`);
        } catch (error) {
            return error.response;
        }
    }

    async buscarHistoricosRecargas(page=1) {
        try {
            return await this.http().get(`recarga/historicos?page=${page}`);
        } catch (error) {
            return error.response;
        }
    }

    async buscarHistoricoSaques(page=1) {
        try {
            return await this.http().get(`saque/historico?page=${page}`);
        } catch (error) {
            return error.response;
        }
    }

    async buscarSolicitacoesDeSaque(page=1) {
        try {
            return await this.http().get(`saques/historico?page=${page}`);
        } catch (error) {
            return error.response;
        }
    }

    async aprovarSaque(valor, saqueId) {
        try {
            return await this.http().post(`saque/${saqueId}/pago`, {valor});
        } catch (error) {
            return error.response;
        }
    }

    async reprovarSaque(motivo, saqueId) {
        try {
            return await this.http().post(`saque/${saqueId}/reprovado`, {motivo});
        } catch (error) {
            return error.response;
        }
    }

}