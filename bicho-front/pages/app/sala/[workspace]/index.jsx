import {useEffect, useState} from "react";
import CircularLoadCustom from "@/components/icons/CircularLoadCustom";
import {toMoney, verificarUsuarioLogado} from "@/helpers/functions";
import SalaServiceAPI from "@/services/SalaServiceAPI";
import SalaEspera from "@/components/SalaEspera/SalaEspera";
import {setCookie} from "cookies-next";
import {toast, ToastContainer} from "react-toastify";
import {useRouter} from "next/router";
import ModalLoginCadastro from "@/components/ModalAuth/ModalAuth";
import Head from "next/head";

const SalaJogo = function() {

    const [salaInformacoes, setSalaInformacoes] = useState();
    const [loading, setLoading] = useState(true);
    const salaServiceAPI = new SalaServiceAPI();
    const router = useRouter();

    useEffect(() => {
        start();
    }, []);// eslint-disable-line react-hooks/exhaustive-deps

    const start = async () => {
        let sala_id = router.query.workspace;
        if(!sala_id) {
            toast.error("Erro ao buscar a sala, tente novamente");
            setLoading(false);
        }
        try {
            const res = await salaServiceAPI.buscarSala(sala_id);
            if(res?.status === 200){
                setLoading(false);
                setSalaInformacoes(res?.data);
            } else {
                throw "Erro ao buscar a sala";
            }
        } catch (ex) {
            if(verificarUsuarioLogado())
                window.location.href = "/app/jogos";
        }
    }

    return (
        <div className="w-full p-6">
            <ToastContainer />

            { loading ? <div className="flex justify-center mt-6">
                <CircularLoadCustom color="#fff"/>
            </div> : ''}

            <Head>
                <title>{salaInformacoes?.nome ? `Sala: ${salaInformacoes?.nome}` : "Sala de jogo"}</title>
            </Head>

            {
                (!loading && salaInformacoes) ? (
                    <SalaEspera salaInformacoes={salaInformacoes} />
                ) : ''
            }
        </div>
    );
}

export default SalaJogo;