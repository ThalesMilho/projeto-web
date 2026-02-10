import "./styles.css";
import {Inter, Poppins, Nunito, Nunito_Sans} from 'next/font/google';
import { useEffect, useState } from "react";
import Header from "@/components/Header/Header";
import MenuInferior from "@/components/MenuInferior/MenuInferior";
import {getCookie} from "cookies-next/client";
import Image from "next/image";
import 'react-toastify/dist/ReactToastify.css';
import React from "react";
import UsuarioServiceAPI from "@/services/UserServiceAPI";
import {toast, ToastContainer} from "react-toastify";
import SocketServiceBase from "@/services/SocketServiceBase";
import 'moment/locale/pt-br';
import MenuLateral from "@/components/MenuLateral/MenuLateral";
import {useRouter} from "next/router";
import {verificarUsuarioLogado} from "@/helpers/functions";
import {usuarioStatus as tipoUsuario} from "@/models/usuario";
import Head from "next/head";

const poppins = Nunito_Sans({
    weight: ['200','300','400','500','600','700','800','900'],
    subsets: ['latin'],
});

export const ContextoUsuario = React.createContext();

export default function MyApp({ Component, pageProps, ...rest }) {

    const socket = new SocketServiceBase();
    const usuarioServiceAPI = new UsuarioServiceAPI();

    const [loadingScreen, setLoadingScreen] = useState(true);
    const [fechandoLoading, setFechandoLoading] = useState(false);
    const [logado, setLogado] = useState(false);
    const [dadosUsuarioLogado, setDadosUsuarioLogado] = useState({tipo: tipoUsuario.admin});

    const router = useRouter();
    const listaLayoutPuro = ['/login', '/cadastro'];
    const ocultarHeaderInicial = ['/app/loteria', '/app/bicho'];

    useEffect(() => {
        const tk = getCookie("authToken");

        if(tk) {
            setLogado(true);
        } else {
            setTimeout(() => {
                setFechandoLoading(true);
                setTimeout(() => {
                    setLoadingScreen(false);
                }, 300);
            }, 1000)
        }

        start(getCookie("authToken"));
    }, []);

    const start = async function(authToken) {
        if(authToken) {
            try {
                const res = await usuarioServiceAPI.buscarDadosUsuarioLogado();

                if(res?.status === 200 && res?.data?.user?.id) {
                    setDadosUsuarioLogado(res.data.user);
                    socket.conectarWebSocket(authToken, res?.data?.user?.id);
                    setFechandoLoading(true);
                    setTimeout(() => {
                        setLoadingScreen(false);
                    }, 500);
                } else {
                    toast.error(res?.data?.message ? res?.data?.message : "Ops, houve algum erro, tente novamente");
                    console.log(getCookie("authToken"));
                }
            } catch(ex) {
            }
        } else {
            socket.conectarWebSocket(null, null);
        }
    }

    if(listaLayoutPuro.includes(router.pathname))
        return <>
            <Head>
                <title>Maior Bicho</title>
            </Head>
            <Component {...pageProps} />
        </>;

    return (
        <main className={poppins.className + " text-base"}>
            <Head>
                <title>Maior Bicho</title>
            </Head>
            <ToastContainer />
            {
                loadingScreen && (
                    <div className={`flex flex-col justify-center items-center absolute w-full h-full z-50 bg-degrade ${fechandoLoading ? "opacity-0" : ""} `} style={{ transition: "all 0.5s ease" }}>
                        <Image src="/images/logo.png" width={3112} height={3976} className="w-2/4 max-w-40" alt="Logo" />
                        <div className="text-white text-3xl font-bold">Maior Bicho</div>
                    </div>
                )
            }

            {
                !loadingScreen && (
                    <ContextoUsuario.Provider value={[dadosUsuarioLogado, setDadosUsuarioLogado]}>
                        <div className="">
                            {
                                !ocultarHeaderInicial.map(e => router.pathname.startsWith(e)).filter(e => e)[0] ? <div>
                                    <Header/>
                                </div> : ''
                            }
                            <div className="">
                                {
                                    verificarUsuarioLogado() ? (
                                        <div className="hidden md:block">
                                            <MenuLateral />
                                        </div>
                                    ) : ''
                                }
                                <div className={`${verificarUsuarioLogado() ? 'md:pl-64 lg:pl-72' : ''} transition-all duration-300`}>
                                    <Component {...pageProps} />
                                </div>
                            </div>
                            {
                                !ocultarHeaderInicial.map(e => router.pathname.startsWith(e)).filter(e => e)[0] ? <>
                                    {
                                        verificarUsuarioLogado() ? (
                                            <MenuInferior/>
                                        ) : ''
                                    }
                                </> : ''
                            }

                        </div>
                    </ContextoUsuario.Provider>
                )
            }

        </main>
    );
}
