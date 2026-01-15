import {useEffect, useState} from "react";
import {toast, ToastContainer} from "react-toastify";
import LoadCenter from "@/components/icons/LoadCenter";
import FinanceiroServiceAPI from "@/services/FinanceiroServiceAPI";
import {formatarCelular, formatarCPF, toMoney} from "@/helpers/functions";
import {status, traduzirStatus} from "@/helpers/saqueStatus";
import moment from "moment";
import CustomButton from "@/components/CustomButton/CustomButton";
import ModalAprovarSaque from "@/components/ModalAprovarSaque/ModalAprovarSaque";
import ModalReprovarSaque from "@/components/ModalReprovarSaque/ModalReprovarSaque";

const SolicitacoesSaquePage = function() {

    const [solicitacoesDeSaque, setSolicitacoesDeSaque] = useState([]);
    const financeiroServiceAPI = new FinanceiroServiceAPI();
    const [loading, setLoading] = useState(true);
    const [openModalAprovarSaque, setOpenModalAprovarSaque] = useState(false);
    const [openModalReprovarSaque, setOpenModalReprovarSaque] = useState(false);
    const [idSaquePagando, setIdSaquePagando] = useState(null);
    const [idSaqueReprovando, setIdSaqueReprovando] = useState(null);

    useEffect(() => {
        start();
    }, []);

    const start = async function() {
        const res = await financeiroServiceAPI.buscarSolicitacoesDeSaque();
        if(res?.status === 200 && res?.data?.solicitacoes?.data) {
            setLoading(false);
            setSolicitacoesDeSaque(res?.data?.solicitacoes?.data);
        } else {
            setLoading(false);
            toast.error("Houve um erro ao buscar as solicitações de saque");
        }
    }

    const handlePago = function(saqueId) {
        setIdSaquePagando(saqueId)
        setOpenModalAprovarSaque(true);
    }

    const handleReprovado = function(saqueId) {
        setIdSaqueReprovando(saqueId)
        setOpenModalReprovarSaque(true);
    }

    const handleClosePago = function(pago) {
        setOpenModalAprovarSaque(false);
        if(pago) {
            start();
        }
    }

    const handleCloseReprovado = function(reprovado) {
        setOpenModalReprovarSaque(false);
        if(reprovado) {
            start();
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
                            openModalAprovarSaque && (
                                <ModalAprovarSaque
                                    onClose={handleClosePago}
                                    saqueId={idSaquePagando}
                                />
                            )
                        }
                        {
                            openModalReprovarSaque && (
                                <ModalReprovarSaque
                                    onClose={handleCloseReprovado}
                                    saqueId={idSaqueReprovando}
                                />
                            )
                        }
                        {
                            solicitacoesDeSaque?.length > 0 ?
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
                                        <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300">Data</th>
                                        <th className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b border-gray-300"></th>
                                    </tr>
                                    </thead>
                                    <tbody>
                                    {solicitacoesDeSaque.map((solicitacao, index) => (
                                        <tr
                                            key={index}
                                            className={`${
                                                index % 2 === 0 ? "bg-white" : "bg-gray-50"
                                            } hover:bg-gray-100`}
                                        >
                                            <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                #{solicitacao?.id}
                                            </td>

                                            <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                {toMoney(solicitacao?.valor)}
                                            </td>

                                            <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                {solicitacao?.user?.name}
                                            </td>

                                            <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                {solicitacao?.user?.documento ? formatarCPF(solicitacao?.user?.documento) : '-'}
                                            </td>

                                            <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                {formatarCelular(solicitacao?.user?.celular)}
                                            </td>

                                            <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                <div className="flex items-center">
                                                    {
                                                        solicitacao.status === status.pago && (
                                                            <div className="bg-success w-3 h-3 rounded-full mr-2"></div>
                                                        )
                                                    }
                                                    {
                                                        solicitacao.status === status.pendente && (
                                                            <div className="bg-warning w-3 h-3 rounded-full mr-2"></div>
                                                        )
                                                    }
                                                    {
                                                        solicitacao.status === status.reprovado && (
                                                            <div className="bg-red-600 w-3 h-3 rounded-full mr-2"></div>
                                                        )
                                                    }
                                                    <span>
                                                        {traduzirStatus(solicitacao.status)}
                                                    </span>
                                                </div>
                                                {
                                                    (solicitacao.status === status.reprovado && solicitacao.descricao) && (
                                                        <small> {solicitacao.descricao}</small>
                                                    )
                                                }
                                            </td>

                                            <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                <small className="whitespace-nowrap">{moment(solicitacao?.created_at).format('DD/MM/YYYY - HH:mm')}</small>
                                            </td>

                                            <td className="px-4 py-2 text-sm text-gray-700 border-b border-gray-300">
                                                <div className="w-fit whitespace-nowrap">
                                                    <div className="mr-2 inline-block">
                                                        <CustomButton disabled={solicitacao.status !== status.pendente}
                                                                      bgColor="bg-success"
                                                                      label="Pago"
                                                                      onClick={e => handlePago(solicitacao?.id)}
                                                        />
                                                    </div>
                                                    <div className="mr-2 inline-block">
                                                        <CustomButton disabled={solicitacao.status !== status.pendente}
                                                                      bgColor="bg-red-500"
                                                                      label="Reprovar"
                                                                      onClick={e => handleReprovado(solicitacao?.id)}
                                                        />
                                                    </div>
                                                </div>
                                            </td>

                                        </tr>
                                    ))}
                                    </tbody>
                                </table>
                                :
                                <div className="flex items-center flex-col">
                                <p className="text-secondary mb-3">Nenhuma solicitação encontrada</p>
                                </div>
                        }
                    </div>
            }
        </div>
    );
}

export default SolicitacoesSaquePage;