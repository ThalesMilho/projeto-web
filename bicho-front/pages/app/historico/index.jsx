import {useEffect, useState} from "react";
import ClockCustom from "@/components/icons/ClockCustom";
import {theme} from "@/tailwind.config";
import {toast, ToastContainer} from "react-toastify";
import LoadCenter from "@/components/icons/LoadCenter";
import moment from "moment/moment";
import {getIdUsuarioLogado, toMoney} from "@/helpers/functions";
import {useRouter} from "next/router";
import SalaServiceAPI from "@/services/SalaServiceAPI";
import Pagination from "@/components/Pagination/Pagination";
import Head from "next/head";

const Historico = function() {

    const [apostas, setApostas] = useState([]);
    const salaServiceAPI = new SalaServiceAPI();
    const [loading, setLoading] = useState(true);
    const [nomeUsuario, setNomeUsuario] = useState("");
    const router = useRouter();
    const [page, setPage] = useState(1);

    useEffect(() => {
        start(router?.query?.user);
    }, []); // eslint-disable-line react-hooks/exhaustive-deps

    const start = async function(usuario_id=null, _pagina=null) {
        const res = await salaServiceAPI.historicoSalas(_pagina ?? 1, usuario_id);
        if(res?.status === 200) {
            setLoading(false);
            setApostas(res?.data);
            // setNomeUsuario(res?.data?.data);
        } else {
            setLoading(false);
            toast.error("Houve um erro ao buscar suas apostas");
        }
    }

    const calcularGanho = function(sala) {
        return (sala.valor_entrada * sala?.quantidade_jogadores) * (sala?.lucro_porcentagem/100);
    }

    const onChangePage = function(page) {
        start(null, page)
    }

    return (
        <div className="container mx-auto p-4">
            <Head>
                <title>Histórico de partidas</title>
            </Head>
            <p className="text-white font-bold mb-4">Histórico de apostas { nomeUsuario && ('- ' + nomeUsuario)}</p>
            <ToastContainer />
            {
                loading ?
                    <LoadCenter/>
                    :
                    <div className="rounded-md overflow-hidden overflow-x-auto">
                        {
                            apostas?.data.length > 0 ?
                                <>
                                    <table
                                        className="table-auto w-full border-collapse border border-gray-300 rounded-md shadow-md">
                                        <thead className="bg-gray-100">
                                        <tr>
                                            <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300">ID</th>
                                            <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300">Qtd. Jogadores</th>
                                            <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300">Valor da sala</th>
                                            <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300">Resultado</th>
                                            <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300">Data de ingresso</th>
                                            <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300">Data do resultado</th>
                                        </tr>
                                        </thead>
                                        <tbody>
                                        {apostas.data.map((aposta, index) => (
                                            <tr
                                                key={index}
                                                className={`${
                                                    index % 2 === 0 ? "bg-white" : "bg-gray-50"
                                                } hover:bg-gray-100`}
                                            >
                                                <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                    #{aposta?.id}
                                                </td>

                                                <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                    {aposta?.sala?.quantidade_jogadores}
                                                </td>

                                                <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                    <span className="font-bold text-success-dark">{toMoney(aposta?.sala.valor_entrada)}</span>
                                                </td>

                                                <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                    {
                                                        aposta?.resultado ?
                                                            (
                                                                String(aposta?.resultado?.vencedor_id) === String(getIdUsuarioLogado()) ?
                                                                    <span
                                                                        className="font-bold text-success-dark">+{toMoney(calcularGanho(aposta.sala))}</span>
                                                                    :
                                                                    <span
                                                                        className="font-bold text-red-500">{toMoney(aposta?.sala.valor_entrada)}</span>
                                                            )
                                                            :
                                                            <span className="font-bold text-yellow-500">Aguardando</span>
                                                    }
                                                </td>

                                                <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                    {moment(aposta?.created_at).format('DD/MM/YYYY HH:mm:ss')}
                                                </td>

                                                <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                    {moment(aposta?.resultado?.created_at).format('DD/MM/YYYY HH:mm:ss')}
                                                </td>
                                            </tr>
                                        ))}
                                        </tbody>
                                    </table>

                                    <Pagination onPageChange={onChangePage} res={apostas} />
                                </>
                                :
                                <div className="flex items-center flex-col">
                                    <p className="text-secondary mb-3">Você ainda não possui apostas</p>
                                    <ClockCustom color={theme.extend.colors.secondary} size={75}/>
                                </div>
                        }
                    </div>
            }
        </div>
    );
}

export default Historico;