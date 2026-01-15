import ServiceAPI from './ServiceBaseAPI.js';

export default class SalaServiceAPI extends ServiceAPI {

    async cadastrarSala(data) {
        try {
            return await this.http().post(`sala`, data);
        } catch (error) {
            return error.response;
        }
    }

    async buscarSalas(data) {
        try {
            return await this.http().get(`sala`, data);
        } catch (error) {
            return error.response;
        }
    }

    async buscarSala(sala_id) {
        try {
            return await this.http().get(`sala/`+sala_id);
        } catch (error) {
            return error.response;
        }
    }

    async participar(sala_id) {
        try {
            return await this.http().post(`sala/${sala_id}/participar`);
        } catch (error) {
            return error.response;
        }
    }

    async historicoSalas(page=1, usuario_id=null) {
        try {
            return await this.http().get(`sala/historico?page=${page}${usuario_id ? '&user_id='+usuario_id : ''}`);
        } catch (error) {
            return error.response;
        }
    }

    async buscarDadosRodada(rodada, sala_id) {
        try {
            return await this.http().get(`sala/${sala_id}/rodada/${rodada}`);
        } catch (error) {
            return error.response;
        }
    }

}