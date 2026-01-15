import CustomInput1 from "@/components/CustomInput/CustomInput1";
import CpfCnpjInput from "@/components/CustomInput/CpfCnpjInput";
import CustomButton from "@/components/CustomButton/CustomButton";
import Image from "next/image";
import Link from "next/link";
import UsuarioServiceAPI from "@/services/UserServiceAPI";
import React, {useState} from "react";
import {setCookie} from "cookies-next";
import { ToastContainer, toast } from 'react-toastify';
import {InputMask} from "@react-input/mask";

const CadastroPage = function() {

    const usuarioServiceAPI = new UsuarioServiceAPI();
    const [nome, setNome] = useState("");
    const [celular, setCelular] = useState("");
    const [senha, setSenha] = useState("");
    const [loading, setLoading] = useState(false);
    const [emailUsuario, setEmailUsuario] = useState("");
    const [cpfUsuario, setCpfUsuario] = useState("");

    const cadastrarUsuario = async function(event) {
        event.preventDefault();

        setLoading(true);
        const res = await usuarioServiceAPI.cadastrarUsuario(nome, celular, senha, emailUsuario, cpfUsuario)

        if(res?.status === 200 && res?.data?.token){
            setCookie("authToken", res.data.token);
            setCookie("usuarioId", res.data.user.id);
            setCookie("usuarioNome", res.data.user.name);
            toast.success("Cadastrado com sucesso!");
            setTimeout(() => {
                window.location.href = "/app/jogos";
            }, 2000)
        } else {
            toast.error(res?.data?.message ? res?.data?.message : "Ops, houve algum erro, tente novamente");
            setLoading(false);
        }
    }

    return (
        <div className="bg-degrade">
            <div className="p-4 flex flex-col justify-center min-h-screen max-w-96 mx-auto">
                <ToastContainer />
                <form className="grid grid-cols-1 gap-4" onSubmit={cadastrarUsuario}>
                    <div className="flex flex-col items-center justify-center">
                        <Image src="/images/logo.png" width={3112} height={3976} className="w-2/4 max-w-28" alt="Logo" />
                        <div className="text-white text-3xl font-bold">Maior Bicho</div>
                    </div>
                    <CustomInput1
                        light
                        disabled={loading}
                        value={nome}
                        onChange={e => setNome(e.target.value)}
                        required
                        name="nome"
                        placeholder="Nome completo"
                        label="Nome completo"
                    />
                    <CustomInput1 light label="E-mail" value={ emailUsuario } onChange={ e => setEmailUsuario(e.target.value) } disabled={loading} required name="email" placeholder="E-mail" />
                    <CpfCnpjInput light inputmode="numeric" label="CPF ou CNPJ" value={ cpfUsuario } onChange={ e => setCpfUsuario(e.target.value) } disabled={loading} required name="cpf" placeholder="CPF ou CNPJ" />
                    <CustomInput1
                        light
                        disabled={loading}
                        value={celular}
                        onChange={e => setCelular(e.target.value)}
                        required
                        name="celular"
                        type="tel"
                        placeholder="Celular (Whatsapp)"
                        mask="(__) _ ____-____" replacement={{ _: /\d/ }}
                        label="Celular (Whatsapp)"
                    />
                    <CustomInput1
                        light
                        disabled={loading}
                        value={senha}
                        onChange={e => setSenha(e.target.value)}
                        required
                        type="password"
                        name="senha"
                        placeholder="Senha"
                        label="Senha de acesso"
                    />
                    <CustomButton bgColor="bg-white" className="!text-primary font-bold" light loading={loading} label="Cadastrar" />
                    <div className="flex justify-center mt-4">
                        <hr className="border-2 rounded-full w-2/4"/>
                    </div>
                    <div>
                        <Link href="/login">
                            <CustomButton type="button" transparent label="Faça login agora mesmo"/>
                        </Link>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default CadastroPage;