import CustomInput1 from "@/components/CustomInput/CustomInput1";
import RadioButton from "@/components/RadioButton/RadioButton";
import {formatarCPF, realToFloat, toMoney } from "@/helpers/functions";
import CustomButton from "@/components/CustomButton/CustomButton";
import {useContext, useEffect, useState} from "react";
import FinanceiroServiceAPI from "@/services/FinanceiroServiceAPI";
import {ContextoUsuario} from "@/pages/_app";
import {toast, ToastContainer} from "react-toastify";
import CircularLoadCustom from "@/components/icons/CircularLoadCustom";
import {status, traduzirStatus} from "@/helpers/saqueStatus";
import moment from "moment";
import CardDetalhes from "@/components/CardDetalhes/CardDetalhes";

const SaquePage = function() {

    const financeiroServiceAPI = new FinanceiroServiceAPI();

    const [valorSaque, setValorSaque] = useState(null);
    const [CPFUsuario, setCPFUsuario] = useState(null);
    const [showValores, setShowValores] = useState(true);
    const [checkRecargaAtivo, setCheckRecargaAtivo] = useState(false);
    const [loadingSaque, setLoadingSaque] = useState(false);
    const [dadosUsuarioLogado] = useContext(ContextoUsuario);

    const [historicoSaque, setHistoricoSaque] = useState([]);
    const [loadingHistorico, setLoadingHistorico] = useState(false);

    useEffect(() => {
        if( dadosUsuarioLogado?.documento ) {
            setCPFUsuario(formatarCPF(dadosUsuarioLogado?.documento));
        }
    }, [dadosUsuarioLogado]);

    const changeValorRecarga = function (valorRecarga) {
        setCheckRecargaAtivo(true);
        setValorSaque(parseFloat(valorRecarga.toString()));
    }

    const changeManualValorRecarga = function(valorRecarga) {
        setValorSaque(valorRecarga);
        if(checkRecargaAtivo){
            setShowValores(false);
            setCheckRecargaAtivo(false);
            setTimeout(() => {
                setShowValores(true);
            }, 100);
        }
    }

    const handleRealizarSaque = async function(event) {
        event.preventDefault();
        setLoadingSaque(true);
        realizarSaque();
    }

    const realizarSaque = async function() {
        const res = await financeiroServiceAPI.realizarSaque(realToFloat(valorSaque));

        if(res?.status === 200) {
            setLoadingSaque(false);
            atualizarHistoricoSaque();
        } else {
            toast.error(res?.data?.message ? res?.data?.message : "Ops, houve algum erro, tente novamente");
            setLoadingSaque(false);
        }
    }


    const atualizarHistoricoSaque = async function() {
        setLoadingHistorico(true);
        const res = await financeiroServiceAPI.buscarHistoricoSaques();
        setLoadingHistorico(false);

        if(res.status === 200) {
            setHistoricoSaque(res.data.data);
        } else {
            toast.error("Erro ao buscar histórico de saques");
        }

    }

    return (
        <>
            <ToastContainer/>
            <form onSubmit={handleRealizarSaque}>
                <div className="grid grid-cols-1 gap-2">
                    <CustomInput1 disabled={loadingSaque} type="tel" required value={valorSaque}
                                  onChange={e => changeManualValorRecarga(e.target.value)} label="Valor do saque (R$)"
                                  placeholder="Insira o valor do saque" currency/>

                    <CustomInput1 disabled mask="___.___.___-__" replacement={{_: /\d/}} type="tel"
                                  required value={CPFUsuario} label="CPF Do titular"/>

                    {
                        showValores && (
                            <div className="grid grid-cols-3 gap-3 my-2">
                                <RadioButton disabled={loadingSaque} onChange={() => changeValorRecarga(10)}
                                             name="recarga_valor" label={toMoney(10)} value={10}/>
                                <RadioButton disabled={loadingSaque} onChange={() => changeValorRecarga(15)}
                                             name="recarga_valor" label={toMoney(15)} value={15}/>
                                <RadioButton disabled={loadingSaque} onChange={() => changeValorRecarga(20)}
                                             name="recarga_valor" label={toMoney(20)} value={20}/>
                                <RadioButton disabled={loadingSaque} onChange={() => changeValorRecarga(50)}
                                             name="recarga_valor" label={toMoney(50)} value={50}/>
                                <RadioButton disabled={loadingSaque} onChange={() => changeValorRecarga(100)}
                                             name="recarga_valor" label={toMoney(100)} value={100}/>
                                <RadioButton disabled={loadingSaque} onChange={() => changeValorRecarga(500)}
                                             name="recarga_valor" label={toMoney(500)} value={500}/>
                            </div>
                        )
                    }

                    <CustomButton loading={loadingSaque} type="submit" label="Realizar saque" bgColor="bg-success-dark"/>
                </div>
            </form>

            {
                (!loadingHistorico && historicoSaque.length === 0) && (
                    <div className="mt-4">
                        <CustomButton onClick={atualizarHistoricoSaque} bgColor="!text-primary shadow-none"
                                      label="Buscar histórico de saques"/>
                    </div>
                )
            }

            {
                (loadingHistorico && historicoSaque.length === 0) && (
                    <div className="flex justify-center mt-6">
                        <CircularLoadCustom color="#fff"/>
                    </div>
                )
            }

            {
                (!loadingHistorico && historicoSaque.length > 0) && (
                    <div>
                        <p className="text-white font-bold mb-4 mt-8">Meus saques</p>
                        <div className="grid gap-2">
                            {
                                historicoSaque.map((saque, index) => {
                                    return (
                                        <CardDetalhes border="border" key={index}>
                                            <div className="w-full">
                                                <div className="w-full flex justify-between">
                                                    <div className="flex items-center">
                                                        {
                                                            saque.status === status.pago && (
                                                                <div className="bg-success w-3 h-3 rounded-full mr-2"></div>
                                                            )
                                                        }
                                                        {
                                                            saque.status === status.pendente && (
                                                                <div className="bg-warning w-3 h-3 rounded-full mr-2"></div>
                                                            )
                                                        }
                                                        {
                                                            saque.status === status.reprovado && (
                                                                <div className="bg-red-600 w-3 h-3 rounded-full mr-2"></div>
                                                            )
                                                        }
                                                        <span>{traduzirStatus(saque.status)}</span>
                                                    </div>
                                                    <div className="ml-2 text-white">#{saque.id}</div>
                                                </div>

                                                <div className="pb-2 pt-4">
                                                    <hr className="border-dashed text-white opacity-50"/>
                                                </div>

                                                <div className="text-sm text-secondary">
                                                    <div>Nome: {dadosUsuarioLogado?.name}</div>
                                                    <div>Data: {moment(saque.created_at).format("DD/MM/YYYY") + " as " + moment(saque.created_at).format("HH:mm")}</div>
                                                    {
                                                        dadosUsuarioLogado?.documento && (
                                                            <div>CPF: {formatarCPF(dadosUsuarioLogado?.documento)}</div>
                                                        )
                                                    }
                                                    <div>Valor: {toMoney(saque.valor)}</div>
                                                    {
                                                        (saque.status === status.reprovado && saque.descricao) && (
                                                            <div>Motivo: {saque?.descricao}</div>
                                                        )
                                                    }
                                                </div>
                                            </div>
                                        </CardDetalhes>
                                    );
                                })
                            }
                        </div>
                    </div>
                )
            }
        </>
    )
        ;
}

export default SaquePage;