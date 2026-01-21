import ServiceAPI from './ServiceBaseAPI.js';

export default class UsuarioServiceAPI extends ServiceAPI {

    async cadastrarUsuario(nome, celular, senha, email, cpf) {
        try {
            return await this.http().post('auth/cadastro', {
                nome,
                celular,
                password: senha,
                email,
                cpf
            });
        } catch (error) {
            return error.response;
        }

    }

    async logarUsuario(login, senha) {
        try {
            return await this.http().post('auth', {
                login,
                password: senha
            });
        } catch (error) {
            return error.response;
        }
    }

    async buscarDadosUsuarioLogado() {
        try {
            return await this.http().get('usuario');
        } catch (error) {
            return error.response;
        }
    }

    async buscarUsuarios(page=1) {
        try {
            return await this.http().get('usuarios?page=' + page);
        } catch (error) {
            return error.response;
        }
    }

    async setAtivo(ativo, userId) {
        try {
            return await this.http().post(`usuarios/ativo/${userId}`, { ativo });
        } catch (error) {
            return error.response;
        }
    }

}