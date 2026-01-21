import { useState, useEffect } from "react";
import {toast, ToastContainer} from "react-toastify";
import CustomInput1 from "@/components/CustomInput/CustomInput1";
import CustomButton from "@/components/CustomButton/CustomButton";
import FinanceiroServiceAPI from "@/services/FinanceiroServiceAPI";

const ModalReprovarSaque = function({ onClose, saqueId }) {

    const financeiroServiceAPI = new FinanceiroServiceAPI();
    const [isVisible, setIsVisible] = useState(false);
    const [loading, setLoading] = useState(false);
    const [motivo, setMotivo] = useState("");

    useEffect(() => {
        setTimeout(() => {
            setIsVisible(true);
        }, 100)
    }, []);

    const onSubmitBoletaAposta = async function(event) {
        event.preventDefault();
        setLoading(true)

        const res = await financeiroServiceAPI.reprovarSaque(motivo, saqueId);

        if(res?.status !== 204) {
            toast.error(res?.data?.message ?? "Erro ao reprovar saque, tente novamente");
            setLoading(false);
        } else {
            toast.success(res?.data?.message ?? "Saque reprovado com sucesso!");
            setTimeout(() => {
                setLoading(false);
                handleClose(true);
            }, 2000 );
        }
    }

    const handleClose = function(cadastrado=false) {
        setIsVisible(false);
        setTimeout(() => {
            onClose(cadastrado);
        }, 300)
    }


    return (
        <div
            className={`relative z-10 ${isVisible ? "opacity-100" : "opacity-0"} transition-opacity duration-300`}
            aria-labelledby="modal-title"
            role="dialog"
            aria-modal="true"
        >
            <ToastContainer />
            <div
                className={`fixed inset-0 bg-gray-500/75 transition-opacity duration-300 ${isVisible ? "opacity-100" : "opacity-0"}`}
                aria-hidden="true"
            ></div>

            <div className="fixed inset-0 z-10 w-screen overflow-y-auto">
                <div className="flex min-h-full items-center justify-center p-6 text-center sm:p-0">
                    <div
                        className={`relative transform overflow-hidden rounded-lg bg-background text-left shadow-xl transition-all duration-300 sm:my-8 sm:w-full sm:max-w-5xl ${
                            isVisible ? "scale-100" : "scale-95"
                        }`}
                    >
                        {/* Botão de fechar */}
                        <button
                            type="button"
                            onClick={() => handleClose(false)}
                            className="absolute top-4 right-4 text-white hover:text-gray-300 focus:outline-none"
                            aria-label="Fechar"
                        >
                            ✖
                        </button>

                        <div className="bg-background px-6 pb-6 pt-8 sm:p-8 sm:pb-6">
                            <form onSubmit={onSubmitBoletaAposta}>
                                <div className="sm:flex sm:items-start">
                                    <div className="text-white font-semibold mb-6 text-lg">Insira o motivo da reprovação</div>
                                </div>

                                <div className="grid grid-cols-1 gap-4">
                                    <CustomInput1
                                                  className="bg-secondary colo"
                                                  label="Motivo"
                                                  required
                                                  disabled={loading}
                                                  onChange={e => setMotivo(e.target.value)}
                                                  value={motivo}
                                                  placeholder="Insira o motivo"
                                    />
                                    <span className="text-secondary">O saldo subtraído do usuário voltará normalmente</span>
                                    <div className="">
                                        <CustomButton label="Reprovar saque" loading={loading}/>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );

};

export default ModalReprovarSaque;
