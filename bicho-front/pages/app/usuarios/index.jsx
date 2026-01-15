import {useEffect, useState} from "react";
import ClockCustom from "@/components/icons/ClockCustom";
import {theme} from "@/tailwind.config";
import {toast, ToastContainer} from "react-toastify";
import LoadCenter from "@/components/icons/LoadCenter";
import moment from "moment/moment";
import {formatarCelular, formatarCPF, toMoney} from "@/helpers/functions";
import UsuarioServiceAPI from "@/services/UserServiceAPI";
import {usuarioStatus} from "@/models/usuario";
import Switch from "@/components/Switch/Switch";
import CustomButton from "@/components/CustomButton/CustomButton";
import Link from "next/link";
import Pagination from "@/components/Pagination/Pagination";
import Head from "next/head";

const UsuariosPage = function() {

    const [usuarios, setUsuarios] = useState([]);
    const usuarioServiceAPI = new UsuarioServiceAPI();
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);

    useEffect(() => {
        start();
    }, []);

    const start = async function(_page=null) {
        const res = await usuarioServiceAPI.buscarUsuarios(_page ?? page);
        if(res?.status === 200 && res?.data?.usuarios?.data) {
            setLoading(false);
            setUsuarios(res?.data?.usuarios);
        } else {
            setLoading(false);
            toast.error("Houve um erro ao buscar usuários");
        }
    }

    const onChangePagination = function(page_number) {
        setPage(page_number);
        start(page_number);
    }

    return (
        <div className="container mx-auto p-4">
            <Head>
                <title>Usuários</title>
            </Head>
            <p className="text-white font-bold mb-4">Usuários cadastrados</p>
            <ToastContainer />
            {
                loading ?
                    <LoadCenter/>
                    :
                    <div className="rounded-md overflow-hidden overflow-x-auto">
                        {
                            usuarios?.data?.length > 0 ?
                                <div>
                                    <table
                                        className="table-auto w-full border-collapse border border-gray-300 rounded-md shadow-md">
                                        <thead className="bg-gray-100">
                                        <tr>
                                            <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300">ID</th>
                                            <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300">Nome</th>
                                            <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300">Saldo</th>
                                            <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300">Celular</th>
                                            <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300">Tipo</th>
                                            <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300">CPF</th>
                                            <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300">Cadastrado em</th>
                                            <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300">Ativo</th>
                                            <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300"></th>
                                        </tr>
                                        </thead>
                                        <tbody>
                                        {usuarios.data.map((usuario, index) => (
                                            <tr
                                                key={index}
                                                className={`${
                                                    index % 2 === 0 ? "bg-white" : "bg-gray-50"
                                                } hover:bg-gray-100`}
                                            >
                                                <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                    #{usuario?.id}
                                                </td>

                                                <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                    {usuario?.name}
                                                </td>

                                                <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                    {usuario?.saldo?.saldo ? toMoney(usuario?.saldo?.saldo) : toMoney(0)}
                                                </td>

                                                <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                    {formatarCelular(usuario?.celular)}
                                                </td>

                                                <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                    {
                                                        (usuario?.tipo === usuarioStatus.admin) && 'Administrador'
                                                    }
                                                    {
                                                        (usuario?.tipo === usuarioStatus.cliente) && 'Cliente'
                                                    }
                                                </td>

                                                <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                    {
                                                        usuario?.documento ? formatarCPF(usuario?.documento) : '-'
                                                    }
                                                </td>

                                                <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                    {moment(usuario?.created_at).format('DD/MM/YYYY - HH:mm')}
                                                </td>

                                                <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                    <UsuarioAtivo ativo={usuario?.ativo} usuarioId={usuario?.id} />
                                                </td>

                                                <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                    <Link href={"/app/historico?user="+usuario?.id} target="_blank">
                                                        <CustomButton label="Ver partidas" />
                                                    </Link>
                                                </td>

                                            </tr>
                                        ))}
                                        </tbody>
                                    </table>
                                    <Pagination res={usuarios} onPageChange={onChangePagination} />
                                </div>
                                :
                                <div className="flex items-center flex-col">
                                    <p className="text-secondary mb-3">Nenhum usuário encontrado</p>
                                </div>
                        }
                    </div>
            }
        </div>
    );
}

const UsuarioAtivo = function({ usuarioId, ativo }) {

    const [ativado, setAtivado] = useState(ativo);
    const usuarioServiceAPI = new UsuarioServiceAPI();

    const changeAtivo = async function () {
        const novoAtivo = ativado ? 0 : 1;
        setAtivado(novoAtivo);
        const res = await usuarioServiceAPI.setAtivo(novoAtivo, usuarioId);
        if(res?.status === 204) {
            toast.success("Alterado com sucesso!");
        } else {
            setAtivado(ativo);
            toast.error("Erro ao solicitar operação");
        }
    }

    return (
        <Switch checked={ativado} onChange={changeAtivo} />
    );
}

export default UsuariosPage;