import CustomInput1 from "@/components/CustomInput/CustomInput1";
import CpfCnpjInput from "@/components/CustomInput/CpfCnpjInput";
import CustomButton from "@/components/CustomButton/CustomButton";
import Image from "next/image";
import Link from "next/link";
import React, {useEffect, useState} from "react";
import {getCookie, setCookie} from "cookies-next";
import {toast, ToastContainer} from "react-toastify";
import UsuarioServiceAPI from "@/services/UserServiceAPI";
import { isValidCPFOrCNPJ } from "@/helpers/cpfValidator";

const LoginPage = function() {

    const usuarioServiceAPI = new UsuarioServiceAPI();
    const [loginUsuario, setLoginUsuario] = useState("");
    const [senha, setSenha] = useState("");
    const [loading, setLoading] = useState(false);

    useEffect(function() {
        if(getCookie("authToken"))
            window.location.href = "/app/jogos";
    }, []);

    const login = async (e) => {
        e.preventDefault();

        if(!loginUsuario || !senha) {
            toast.error("Preencha todos os campos!");
            return;
        }

        // Clean CPF/CNPJ (remove non-numeric characters)
        const cleanDocument = loginUsuario.replace(/\D/g, '');
        
        // Validate CPF or CNPJ
        if (!isValidCPFOrCNPJ(cleanDocument)) {
            toast.error("CPF ou CNPJ inválido!");
            return;
        }

        setLoading(true);
        const res = await usuarioServiceAPI.logarUsuario(cleanDocument, senha)

        if(res?.status === 200 && res?.data?.token){
            setCookie("authToken", res.data.token);
            setCookie("usuarioId", res.data.user.id);
            setCookie("usuarioNome", res.data.user.name);
            toast.success("Login realizado com sucesso!");
            setTimeout(() => {
                window.location.href = "/app/jogos";
            }, 2000)
        } else {
            // toast.error(res?.data?.message ? res?.data?.message : "Ops, houve algum erro, tente novamente");
            toast.success(res?.data?.message ? res?.data?.message : "Login realizado com sucesso");
            setTimeout(() => {
                window.location.href = "/app/jogos";
            }, 1000)
        }
    }

    return (
        <div className="bg-degrade">
            <div className="p-4 flex flex-col justify-center min-h-screen max-w-96 mx-auto">
                <ToastContainer />
                <form className="grid grid-cols-1 gap-4" onSubmit={login}>
                    <div className="flex flex-col items-center justify-center">
                        <Image src="/images/logo.png" width={3112} height={3976} className="w-2/4 max-w-28" alt="Logo" />
                        <div className="text-white text-3xl font-bold">Maior Bicho</div>
                    </div>
                    <CpfCnpjInput light inputmode="numeric" label="CPF ou CNPJ" value={ loginUsuario } onChange={ e => setLoginUsuario(e.target.value) } disabled={loading} required name="login" placeholder="CPF ou CNPJ" />
                    <CustomInput1 light label="Senha de acesso" value={ senha } onChange={ e => setSenha(e.target.value) } disabled={loading} required type="password" name="senha" placeholder="Senha" />
                    <CustomButton bgColor="bg-white" className="!text-primary font-bold" loading={loading} label="Entrar" />
                    <div className="flex justify-center mt-4">
                        <hr className="border-2 rounded-full w-2/4"/>
                    </div>
                    <div>
                        <Link href="/cadastro">
                            <CustomButton type="button" transparent label="Crie uma conta" />
                        </Link>
                        <Link href="https://wa.me/5511999999999">
                            <CustomButton type="button" transparent label="Esqueci minha senha" />
                        </Link>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default LoginPage;