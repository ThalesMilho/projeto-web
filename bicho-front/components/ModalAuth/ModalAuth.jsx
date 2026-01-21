import { useState, useEffect } from "react";
import CustomInput1 from "@/components/CustomInput/CustomInput1";
import CpfCnpjInput from "@/components/CustomInput/CpfCnpjInput";
import CustomButton from "@/components/CustomButton/CustomButton";
import { toast, ToastContainer } from "react-toastify";
import UsuarioServiceAPI from "@/services/UserServiceAPI";
import { setCookie } from "cookies-next";
import Image from "next/image";

const ModalLoginCadastro = function({ onClose }) {

    const usuarioServiceAPI = new UsuarioServiceAPI();
    const [isVisible, setIsVisible] = useState(false);
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState("login");

    // Estados do Login
    const [loginUsuario, setLoginUsuario] = useState("");
    const [senhaLogin, setSenhaLogin] = useState("");

    // Estados do Cadastro
    const [nome, setNome] = useState("");
    const [celular, setCelular] = useState("");
    const [senha, setSenha] = useState("");
    const [emailUsuario, setEmailUsuario] = useState("");
    const [cpfUsuario, setCpfUsuario] = useState("");

    useEffect(() => {
        setIsVisible(true);
        return () => {
            setIsVisible(false);
        };
    }, []);

    const login = async function(event) {
        event.preventDefault();

        setLoading(true);
        const res = await usuarioServiceAPI.logarUsuario(loginUsuario, senhaLogin);

        if(res?.status === 200 && res?.data?.token){
            setCookie("authToken", res.data.token);
            setCookie("usuarioId", res.data.user.id);
            setCookie("usuarioNome", res.data.user.name);
            toast.success("Login realizado com sucesso!");
            setTimeout(() => {
                let url = window.location.href;
                if (url.indexOf('?') > -1){
                    url += '&enter=1'
                } else {
                    url += '?enter=1'
                }
                window.location.href = url;
            }, 2000);
        } else {
            toast.error(res?.data?.message ? res?.data?.message : "Ops, houve algum erro, tente novamente");
            setLoading(false);
        }
    }

    const cadastrarUsuario = async function(event) {
        event.preventDefault();

        setLoading(true);
        const res = await usuarioServiceAPI.cadastrarUsuario(nome, celular, senha, emailUsuario, cpfUsuario);

        if(res?.status === 200 && res?.data?.token){
            setCookie("authToken", res.data.token);
            setCookie("usuarioId", res.data.user.id);
            setCookie("usuarioNome", res.data.user.name);
            toast.success("Cadastrado com sucesso!");
            setTimeout(() => {
                let url = window.location.href;
                if (url.indexOf('?') > -1){
                    url += '&enter=1'
                } else {
                    url += '?enter=1'
                }
                window.location.href = url;
            }, 2000);
        } else {
            toast.error(res?.data?.message ? res?.data?.message : "Ops, houve algum erro, tente novamente");
            setLoading(false);
        }
    }

    return (
        <div
            className={`relative z-10 ${isVisible ? "opacity-100" : "opacity-0"} transition-opacity duration-300`}
            aria-labelledby="modal-title"
            role="dialog"
            aria-modal="true"
        >
            <ToastContainer />
            <div
                className={`fixed inset-0 bg-gray-500/75 transition-opacity duration-300 ${isVisible ? "opacity-100" : "opacity-0"}`}
                aria-hidden="true"
            ></div>

            <div className="fixed inset-0 z-10 w-screen overflow-y-auto">
                <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
                    <div
                        className={`relative transform overflow-hidden rounded-lg bg-background text-left shadow-xl transition-all duration-300 sm:my-8 sm:w-full sm:max-w-lg ${
                            isVisible ? "scale-100" : "scale-95"
                        }`}
                    >
                        {/* Botão de fechar */}
                        <button
                            type="button"
                            onClick={onClose}
                            className="absolute top-4 right-4 text-white hover:text-gray-300 focus:outline-none z-20"
                            aria-label="Fechar"
                        >
                            ✖
                        </button>

                        <div className="bg-background px-4 pb-4 pt-5 sm:p-6 sm:pb-4">
                            {/* Logo */}
                            <div className="flex justify-center mb-4">
                                <Image src="/images/logo.png" width={3112} height={3976} className="w-2/4 max-w-20" alt="Logo" />
                            </div>

                            {/* Tabs */}
                            <div className="w-full">
                                <div className="flex space-x-4 border-b-2 border-primary">
                                    <button
                                        className={`py-2 px-4 ${
                                            activeTab === "login"
                                                ? "border-b-4 border-primary text-primary font-bold"
                                                : "text-secondary font-semibold"
                                        }`}
                                        onClick={() => setActiveTab("login")}
                                        disabled={loading}
                                    >
                                        Fazer Login
                                    </button>
                                    <button
                                        className={`py-2 px-4 ${
                                            activeTab === "cadastro"
                                                ? "border-b-4 border-primary text-primary font-bold"
                                                : "text-secondary font-semibold"
                                        }`}
                                        onClick={() => setActiveTab("cadastro")}
                                        disabled={loading}
                                    >
                                        Criar Conta
                                    </button>
                                </div>

                                {/* Tab Content */}
                                <div className="mt-4">
                                    {activeTab === "login" && (
                                        <div className="fade-in">
                                            <form onSubmit={login}>
                                                <div className="grid grid-cols-1 gap-3">
                                                    <CpfCnpjInput
                                                        inputmode="numeric"
                                                        label="CPF ou CNPJ"
                                                        value={loginUsuario}
                                                        onChange={e => setLoginUsuario(e.target.value)}
                                                        disabled={loading}
                                                        required
                                                        name="login"
                                                        placeholder="CPF ou CNPJ"
                                                    />
                                                    <CustomInput1
                                                        label="Senha de acesso"
                                                        value={senhaLogin}
                                                        onChange={e => setSenhaLogin(e.target.value)}
                                                        disabled={loading}
                                                        required
                                                        type="password"
                                                        name="senha"
                                                        placeholder="Senha"
                                                    />
                                                    <div className="pt-2">
                                                        <CustomButton loading={loading} type="submit" label="Entrar" />
                                                    </div>
                                                </div>
                                            </form>
                                        </div>
                                    )}
                                    {activeTab === "cadastro" && (
                                        <div className="fade-in">
                                            <form onSubmit={cadastrarUsuario}>
                                                <div className="grid grid-cols-1 gap-3">
                                                    <CustomInput1
                                                        disabled={loading}
                                                        value={nome}
                                                        onChange={e => setNome(e.target.value)}
                                                        required
                                                        name="nome"
                                                        placeholder="Nome completo"
                                                        label="Nome completo"
                                                    />
                                                    <CustomInput1
                                                        label="E-mail"
                                                        value={emailUsuario}
                                                        onChange={e => setEmailUsuario(e.target.value)}
                                                        disabled={loading}
                                                        required
                                                        name="email"
                                                        placeholder="E-mail"
                                                    />
                                                    <CpfCnpjInput
                                                        inputmode="numeric"
                                                        label="CPF ou CNPJ"
                                                        value={cpfUsuario}
                                                        onChange={e => setCpfUsuario(e.target.value)}
                                                        disabled={loading}
                                                        required
                                                        name="cpf"
                                                        placeholder="CPF ou CNPJ"
                                                    />
                                                    <CustomInput1
                                                        disabled={loading}
                                                        value={celular}
                                                        onChange={e => setCelular(e.target.value)}
                                                        required
                                                        name="celular"
                                                        type="tel"
                                                        placeholder="Celular (Whatsapp)"
                                                        mask="(__) _ ____-____"
                                                        replacement={{ _: /\d/ }}
                                                        label="Celular (Whatsapp)"
                                                    />
                                                    <CustomInput1
                                                        disabled={loading}
                                                        value={senha}
                                                        onChange={e => setSenha(e.target.value)}
                                                        required
                                                        type="password"
                                                        name="senha"
                                                        placeholder="Senha"
                                                        label="Senha de acesso"
                                                    />
                                                    <div className="pt-2">
                                                        <CustomButton loading={loading} type="submit" label="Cadastrar" />
                                                    </div>
                                                </div>
                                            </form>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ModalLoginCadastro;