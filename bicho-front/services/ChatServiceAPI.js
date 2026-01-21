import ServiceAPI from './ServiceBaseAPI.js';

export default class ChatServiceAPI extends ServiceAPI {

    async buscarConversasChat(sala_id) {
        try {
            return await this.http().get(`sala/${sala_id}/chat`);
        } catch (error) {
            return error.response;
        }
    }

    async enviarMensagemChat(sala_id, data) {
        try {
            return await this.http().post(`sala/${sala_id}/chat`, data);
        } catch (error) {
            return error.response;
        }
    }

}