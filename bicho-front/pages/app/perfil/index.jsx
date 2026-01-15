import CustomButton from "@/components/CustomButton/CustomButton";
import {deleteCookie} from "cookies-next";
import CustomInput1 from "@/components/CustomInput/CustomInput1";
import {useContext, useEffect, useState} from "react";
import {ContextoUsuario} from "@/pages/_app";
import {formatarCelular} from "@/helpers/functions";
import Head from "next/head";

const Perfil = function() {

    const [dadosUsuarioLogado] = useContext(ContextoUsuario);
    const [nome, setNome] = useState("");
    const [celular, setCelular] = useState("");

    useEffect(() => {
        setNome(dadosUsuarioLogado?.name ?? "");
        setCelular(dadosUsuarioLogado?.celular ?? "");
    }, [dadosUsuarioLogado]);

    const logout = function() {
        deleteCookie("authToken");
        deleteCookie("usuarioId");
        deleteCookie("usuarioNome");
        window.location.href = "/login";
    }

    return (
        <div className="container mx-auto p-4">
            <Head>
                <title>Meu perfil</title>
            </Head>
            <p className="font-bold mb-4">Minhas informações</p>
            <div className="grid grid-cols-1 gap-2">
                <CustomInput1 disabled placeholder="Nome completo" label="Nome completo" value={nome} />
                <CustomInput1 disabled placeholder="E-mail" label="E-mail" value={nome} />
                <CustomInput1 disabled placeholder="Documento" label="CPF ou CNPJ" value={nome} />
                <CustomInput1 disabled placeholder="Telefone" label="Telefone celular" value={formatarCelular(celular)} />
                <div className="mt-2">
                    <CustomButton label="Sair" className="bg-red-500" onClick={logout} />
                </div>
            </div>
        </div>
    );
}

export default Perfil;