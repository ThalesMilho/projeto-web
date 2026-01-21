import {useEffect, useState} from "react";
import {toast, ToastContainer} from "react-toastify";
import LoadCenter from "@/components/icons/LoadCenter";
import FinanceiroServiceAPI from "@/services/FinanceiroServiceAPI";
import {formatarCelular, formatarCPF, toMoney} from "@/helpers/functions";
import {status, traduzirStatus} from "@/helpers/recargaStatus";
import moment from "moment";

const RecargasUsuarios = function() {

    const [recargas, setRecargas] = useState([]);
    const financeiroServiceAPI = new FinanceiroServiceAPI();
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        start();
    }, []);

    const start = async function() {
        const res = await financeiroServiceAPI.buscarHistoricosRecargas();
        if(res?.status === 200 && res?.data?.recargas?.data) {
            setLoading(false);
            setRecargas(res?.data?.recargas?.data);
        } else {
            setLoading(false);
            toast.error("Houve um erro ao buscar as recargas");
        }
    }

    return (
        <div className="container mx-auto p-4">
            <ToastContainer />
            {
                loading ?
                    <LoadCenter/>
                    :
                    <div className="rounded-md overflow-hidden overflow-x-auto">
                        {
                            recargas?.length > 0 ?
                                <table
                                    className="table-auto w-full border-collapse border border-gray-300 rounded-md shadow-md">
                                    <thead className="bg-gray-100">
                                    <tr>
                                        <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300">ID</th>
                                        <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300">Valor</th>
                                        <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300">CPF</th>
                                        <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300">Usuário</th>
                                        <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300">Telefone</th>
                                        <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300">Status</th>
                                        <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300">Checkout ID</th>
                                        <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300">Data</th>
                                    </tr>
                                    </thead>
                                    <tbody>
                                    {recargas.map((recarga, index) => (
                                        <tr
                                            key={index}
                                            className={`${
                                                index % 2 === 0 ? "bg-white" : "bg-gray-50"
                                            } hover:bg-gray-100`}
                                        >
                                            <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                #{recarga?.id}
                                            </td>

                                            <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                {toMoney(recarga?.valor)}
                                            </td>

                                            <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                {recarga?.cpf ? formatarCPF(recarga?.cpf) : '-'}
                                            </td>

                                            <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                {recarga?.user?.name}
                                            </td>

                                            <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                {recarga?.user?.celular ? formatarCelular(recarga?.user?.celular) : '-'}
                                            </td>

                                            <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                <div className="flex items-center">
                                                    {
                                                        recarga.status === status.pago && (
                                                            <div className="bg-success w-3 h-3 rounded-full mr-2"></div>
                                                        )
                                                    }
                                                    {
                                                        recarga.status === status.pendente && (
                                                            <div className="bg-warning w-3 h-3 rounded-full mr-2"></div>
                                                        )
                                                    }
                                                    {
                                                        (recarga.status === status.cancelado || recarga.status === status.devolvido) && (
                                                            <div className="bg-red-600 w-3 h-3 rounded-full mr-2"></div>
                                                        )
                                                    }
                                                    <span>
                                                        {traduzirStatus(recarga.status)}
                                                    </span>
                                                </div>
                                            </td>

                                            <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                {recarga?.checkout_id}
                                            </td>

                                            <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                <small
                                                    className="whitespace-nowrap">{moment(recarga?.created_at).format('DD/MM/YYYY - HH:mm')}</small>
                                            </td>

                                        </tr>
                                    ))}
                                    </tbody>
                                </table>
                                :
                                <div className="flex items-center flex-col">
                                    <p className="text-secondary mb-3">Nenhuma recarga encontrada</p>
                                </div>
                        }
                    </div>
            }
        </div>
    );
}

export default RecargasUsuarios;