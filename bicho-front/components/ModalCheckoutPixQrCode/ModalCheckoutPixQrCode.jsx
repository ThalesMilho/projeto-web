import { useState, useEffect } from "react";
import CustomButton from "@/components/CustomButton/CustomButton";
import Image from "next/image";
import QRCode from "react-qr-code";
import { formatarCPF, toMoney } from "@/helpers/functions";
import { CopyToClipboard } from "react-copy-to-clipboard/src";
import { toast, ToastContainer } from "react-toastify";

const ModalCheckoutPixQrCode = function({ modal=true, action, voltar, qrCode, documento = "", nome = "", valor = 0, recarga_id, hideKeyboard }) {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        setIsVisible(true);
        if (recarga_id) {
            console.log(
                recarga_id,
                window.Echo.private(`recarga.${recarga_id}`).listen(".status_atualizado", atualizarStatusRecarga)
            );
        }
        return () => {
            window.Echo.leave(`recarga.${recarga_id}`);
            setIsVisible(false);
        };
    }, []);

    const atualizarStatusRecarga = function (data) {
        if (data?.status === "pago") {
            voltar({ toast: { type: "success", title: "Pagamento Finalizado!", message: "Pagamento realizado com sucesso!" } });
        }
    };

    const copiadoComSucesso = function () {
        toast.success("Pix copia e cola copiado com sucesso!");
    };

    const ConteudoModal = function() {
        return (
            <>
                <div className={`bg-background pb-4 ${modal ? 'px-4 pt-5 sm:p-6' : ''} sm:pb-4`}>
                    <div className="text-white font-semibold mb-4">Realize o pagamento via PIX</div>
                    <div className="sm:flex sm:items-start">
                        <div className="text-white">
                            {qrCode && <QRCode value={qrCode} bgColor="transparent" fgColor="white" />}
                            <div className="flex items-center pt-4">
                                <div className="bg-warning box-shadow-warning-1 w-3 h-3 rounded-full mr-2"></div>
                                <span className="font-semibold">Aguardando pagamento</span>
                            </div>
                            <span className="text-sm text-center">Não saia dessa tela</span>
                            <div className="flex justify-center my-4">
                                <hr className="border-2 rounded-full w-2/4" />
                            </div>
                            <div>Documento: {formatarCPF(documento) ?? ""}</div>
                            <div>Nome: {nome}</div>
                            <div>Valor: {toMoney(valor)}</div>
                        </div>
                    </div>
                </div>

                <div className={`bg-background px-4 ${!modal ? '' : 'pb-3'} sm:px-6 grid grid-cols-1`}>
                    <div>
                        <CopyToClipboard onCopy={copiadoComSucesso} text={qrCode}>
                            <CustomButton label="Copiar PIX copia e cola" />
                        </CopyToClipboard>
                    </div>
                    <div className="mt-2">
                        <CustomButton label="Voltar" onClick={voltar} transparent={true} />
                    </div>
                </div>
            </>
        );
    }

    if(!modal && hideKeyboard) {
        hideKeyboard();
        return ConteudoModal();
    }

    return (
        <div
            className={`relative z-10 ${isVisible ? "opacity-100" : "opacity-0"} transition-opacity duration-300`}
            aria-labelledby="modal-title"
            role="dialog"
            aria-modal="true"
        >
            <div
                className={`fixed inset-0 bg-gray-500/75 transition-opacity duration-300 ${isVisible ? "opacity-100" : "opacity-0"}`}
                aria-hidden="true"
            ></div>

            <div className="fixed inset-0 z-10 w-screen overflow-y-auto">
                <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
                    <div
                        className={`relative transform overflow-hidden rounded-lg bg-background text-left shadow-xl transition-all duration-300 sm:my-8 ${
                            isVisible ? "scale-100" : "scale-95"
                        }`}
                    >
                        <ConteudoModal />
                    </div>
                </div>
            </div>
        </div>
    );
};


export default ModalCheckoutPixQrCode;
