import { useState, useEffect } from "react";
import {ToastContainer} from "react-toastify";
import Recarga from "@/pages/app/financeiro/Recarga";

const ModalRealizarRecargaFull = function({onClose}) {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        // Trigger fade in após o componente montar
        setTimeout(() => setIsVisible(true), 100);
    }, []);

    const handleClose = () => {
        setIsVisible(false);
        // Aguarda a animação terminar antes de fechar
        setTimeout(() => onClose(), 300);
    };

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
                onClick={handleClose}
            ></div>

            <div className="fixed inset-0 z-10 w-screen overflow-y-auto overflow-x-hidden">
                <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
                    <div
                        className={`relative transform  rounded-lg bg-background text-left shadow-xl transition-all duration-300 sm:my-8 sm:max-w-md ${
                            isVisible ? "opacity-100 scale-100 translate-y-0" : "opacity-0 scale-95 translate-y-4"
                        }`}
                    >
                        {/* Botão de fechar */}
                        <button
                            type="button"
                            onClick={handleClose}
                            className="absolute top-4 right-4 text-white hover:text-gray-300 focus:outline-none z-10 transition-colors"
                            aria-label="Fechar"
                        >
                            ✖
                        </button>

                        <div className="bg-background px-6 pb-6 pt-6 rounded-lg">
                            {/* Header com ícone de troféu */}
                            <div className="">
                                <Recarga modal={false} historico={false} />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ModalRealizarRecargaFull;