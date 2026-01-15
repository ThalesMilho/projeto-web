import CustomInput1 from "@/components/CustomInput/CustomInput1";
import RadioButton from "@/components/RadioButton/RadioButton";
import {formatarCPF, realToFloat, toMoney, validarCPF} from "@/helpers/functions";
import CustomButton from "@/components/CustomButton/CustomButton";
import {useContext, useEffect, useState} from "react";
import FinanceiroServiceAPI from "@/services/FinanceiroServiceAPI";
import {toast, ToastContainer} from "react-toastify";
import ModalValidarDocumento from "@/components/ModalValidarDocumento/ModalValidarDocumento";
import ModalCheckoutPixQrCode from "@/components/ModalCheckoutPixQrCode/ModalCheckoutPixQrCode";
import CircularLoadCustom from "@/components/icons/CircularLoadCustom";
import {status, traduzirStatus} from "@/helpers/recargaStatus";
import moment from "moment";
import CardDetalhes from "@/components/CardDetalhes/CardDetalhes";
import {ContextoUsuario} from "@/pages/_app";

const RecargaPage = function({ historico=true, modal=true }) {

    const financeiroServiceAPI = new FinanceiroServiceAPI();

    const [valorRecarga, setValorRecarga] = useState(null);
    const [CPFUsuario, setCPFUsuario] = useState(null);
    const [showValores, setShowValores] = useState(true);
    const [checkRecargaAtivo, setCheckRecargaAtivo] = useState(false);
    const [loadingRecarga, setLoadingRecarga] = useState(false);
    const [documentoVerificado, setDocumentoVerificado] = useState(false);
    const [openModalValidarDocumento, setOpenModalValidarDocumento] = useState(false);
    const [openModalPixQrCode, setOpenModalPixQrCode] = useState(false);
    const [pixQrCode, setPixQrCode] = useState("");
    const [nomeUsuario, setNomeUsuario] = useState("");
    const [dadosUsuarioLogado] = useContext(ContextoUsuario);
    const [idRecargaAguardandoResposta, setIdRecargaAguardandoResposta] = useState(null);
    const [showKeyboard, setShowKeyboard] = useState(true);

    const [historicoRecarga, setHistoricoRecarga] = useState([]);
    const [loadingHistorico, setLoadingHistorico] = useState(false);

    useEffect(() => {
        if( dadosUsuarioLogado?.documento ) {
            setDocumentoVerificado(true);
            setCPFUsuario(dadosUsuarioLogado?.documento);
        }

        if( dadosUsuarioLogado?.name && !nomeUsuario ) {
            setNomeUsuario(dadosUsuarioLogado.name);
        }
    }, [dadosUsuarioLogado]);// eslint-disable-line react-hooks/exhaustive-deps

    useEffect(() => {
        // atualizarHistoricoRecarga();
    }, []);// eslint-disable-line react-hooks/exhaustive-deps

    const changeValorRecarga = function (valorRecarga) {
        setCheckRecargaAtivo(true);
        setValorRecarga(parseFloat(valorRecarga.toString()));
    }

    const changeManualValorRecarga = function(valorRecarga) {
        setValorRecarga(valorRecarga);
        if(checkRecargaAtivo){
            setShowValores(false);
            setCheckRecargaAtivo(false);
            setTimeout(() => {
                setShowValores(true);
            }, 100);
        }
    }

    const handleRealizarRecarga = async function(event) {
        event.preventDefault();
        setLoadingRecarga(true);
        if( !documentoVerificado && !validarCPF(CPFUsuario) ) {
            setLoadingRecarga(false);
            toast.error("CPF Inválido, verifique novamente");
        } else {
            if(documentoVerificado){
                realizarRecarga();
            } else {
                setOpenModalValidarDocumento(true);
            }
        }
    }

    const realizarRecarga = async function() {
        if(openModalValidarDocumento)
            setOpenModalValidarDocumento(false);
        // const res = await financeiroServiceAPI.realizarRecarga(realToFloat(valorRecarga), CPFUsuario);
        //
        // if(res.status === 200) {
        //     setPixQrCode(res.data.qrcode);
        //     setIdRecargaAguardandoResposta(res.data.recarga.id);
        //     setOpenModalPixQrCode(true);
        // } else {
        //     toast.error(res?.data?.message ? res?.data?.message : "Ops, houve algum erro, tente novamente");
        //     setLoadingRecarga(false);
        // }
    }

    const voltarValidacaoDocumentoModal = function() {
        setOpenModalValidarDocumento(false);
        setLoadingRecarga(false);
    }

    const voltarModalPixQrCode = function(data=null) {
        if(data && data?.toast) {
            if(data.toast.type === "success") {
                toast.success(data.toast.title, data.toast.message);
            } else if (data.toast.type === "error") {
                toast.error(data.toast.title, data.toast.message);
            }
        }
        setShowKeyboard(true);
        setOpenModalPixQrCode(false);
        setLoadingRecarga(false);
    }

    const atualizarHistoricoRecarga = async function() {
        setLoadingHistorico(true);
        const res = await financeiroServiceAPI.buscarHistoricoRecarga();
        setLoadingHistorico(false);

        if(res.status === 200) {
            setHistoricoRecarga(res.data.data);
        } else {
            toast.error("Erro ao buscar histórico de recargas");
        }

    }

    return (
        <>
            <ToastContainer/>

            {
                openModalValidarDocumento && (<ModalValidarDocumento
                    action={realizarRecarga}
                    voltar={voltarValidacaoDocumentoModal}
                />)
            }

            {
                openModalPixQrCode && (<ModalCheckoutPixQrCode
                    hideKeyboard={() => setShowKeyboard(false)}
                    modal={modal}
                    nome={nomeUsuario}
                    documento={CPFUsuario ?? ""}
                    valor={realToFloat(valorRecarga)}
                    qrCode={pixQrCode}
                    voltar={voltarModalPixQrCode}
                    recarga_id={idRecargaAguardandoResposta}
                />)
            }

            {
                showKeyboard ? (
                    <form onSubmit={handleRealizarRecarga}>
                        <div className="grid grid-cols-1 gap-2">
                            <CustomInput1 disabled={loadingRecarga} type="tel" required value={valorRecarga}
                                          onChange={e => changeManualValorRecarga(e.target.value)}
                                          label={<span className="text-gray-900 font-bold">Valor da recarga (R$)</span>}
                                          placeholder="Insira o valor da recarga" currency/>
                            {
                                !documentoVerificado && (
                                    <CustomInput1 mask="___.___.___-__" replacement={{_: /\d/}} disabled={loadingRecarga}
                                                  type="tel"
                                                  required value={CPFUsuario} onChange={e => setCPFUsuario(e.target.value)}
                                                  label={<span className="text-gray-900 font-bold">CPF Do titular</span>} placeholder="Insira o seu CPF"/>
                                )
                            }

                            {
                                showValores && (
                                    <div className="grid grid-cols-3 gap-3 my-2">
                                        <RadioButton disabled={loadingRecarga} onChange={() => changeValorRecarga(10)}
                                                     name="recarga_valor" label={toMoney(10)} value={10}/>
                                        <RadioButton disabled={loadingRecarga} onChange={() => changeValorRecarga(15)}
                                                     name="recarga_valor" label={toMoney(15)} value={15}/>
                                        <RadioButton disabled={loadingRecarga} onChange={() => changeValorRecarga(20)}
                                                     name="recarga_valor" label={toMoney(20)} value={20}/>
                                        <RadioButton disabled={loadingRecarga} onChange={() => changeValorRecarga(50)}
                                                     name="recarga_valor" label={toMoney(50)} value={50}/>
                                        <RadioButton disabled={loadingRecarga} onChange={() => changeValorRecarga(100)}
                                                     name="recarga_valor" label={toMoney(100)} value={100}/>
                                        <RadioButton disabled={loadingRecarga} onChange={() => changeValorRecarga(500)}
                                                     name="recarga_valor" label={toMoney(500)} value={500}/>
                                    </div>
                                )
                            }

                            <CustomButton loading={loadingRecarga} type="submit" label="Recarregar agora"/>
                        </div>
                    </form>
                ) : ''
            }

            {
                (historico == true && (!loadingHistorico && historicoRecarga.length === 0)) && (
                    <div className="mt-4">
                        <CustomButton onClick={atualizarHistoricoRecarga} bgColor="!text-primary shadow-none"
                                      label="Buscar histórico de recargas"/>
                    </div>
                )
            }

            {
                (loadingHistorico && historicoRecarga.length === 0) && (
                    <div className="flex justify-center mt-6">
                        <CircularLoadCustom color="#fff"/>
                    </div>
                )
            }

            {
                (!loadingHistorico && historicoRecarga.length > 0) && (
                    <div>
                        <p className="text-white font-bold mb-4 mt-8">Minhas recargas</p>
                        <div className="grid gap-2">
                            {
                                historicoRecarga.map((recarga, index) => {
                                    return (
                                        <CardDetalhes border="border" key={index}>
                                            <div className="w-full">
                                                <div className="w-full flex justify-between">
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
                                                        <span>{traduzirStatus(recarga.status)}</span>
                                                    </div>
                                                    <div className="ml-2 text-white">#{recarga.id}</div>
                                                </div>

                                                <div className="pb-2 pt-4">
                                                    <hr className="border-dashed text-white opacity-50"/>
                                                </div>

                                                <div className="text-sm text-secondary">
                                                    <div>Nome: {recarga.nome}</div>
                                                    <div>Data: {moment(recarga.created_at).format("DD/MM/YYYY") + " as " + moment(recarga.created_at).format("HH:mm")}</div>
                                                    <div>CPF: {formatarCPF(recarga.cpf)}</div>
                                                    <div>Valor: {toMoney(recarga.valor)}</div>
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

export default RecargaPage;