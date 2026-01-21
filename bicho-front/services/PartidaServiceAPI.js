import ServiceAPI from './ServiceBaseAPI.js';

export default class PartidaServiceAPI extends ServiceAPI {

    async cadastrarPartida(timeCasa, timeFora, dataInicio, horaInicio, tiposApostasSelecionados) {
        try {
            return await this.http().post(`partida`, {
                time_casa: timeCasa,
                time_fora: timeFora,
                data_inicio: dataInicio,
                hora_inicio: horaInicio,
                tipos_apostas: tiposApostasSelecionados
            });
        } catch (error) {
            return error.response;
        }
    }

    async buscarPartidas(page=1) {
        try {
            return await this.http().get(`partida?page=${page}`);
        } catch (error) {
            return error.response;
        }
    }

    async buscarPartida(partida_id) {
        try {
            return await this.http().get(`partida/${partida_id}`);
        } catch (error) {
            return error.response;
        }
    }

    async alterarStatusPartida(partida_id, status) {
        try {
            return await this.http().post(`partida/${partida_id}/status`, {
                status
            });
        } catch (error) {
            return error.response;
        }
    }

}