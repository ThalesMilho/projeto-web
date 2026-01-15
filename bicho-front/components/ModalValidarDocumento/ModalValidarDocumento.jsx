import { useState, useEffect } from "react";
import CustomButton from "@/components/CustomButton/CustomButton";

const ModalValidarDocumento = function({ action, voltar }) {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        // Ativa o fade-in ao montar o componente
        setIsVisible(true);
        return () => {
            // Limpa o estado ao desmontar o componente
            setIsVisible(false);
        };
    }, []);

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
                        className={`relative transform overflow-hidden rounded-lg bg-background text-left shadow-xl transition-all duration-300 sm:my-8 sm:w-full sm:max-w-lg ${
                            isVisible ? "scale-100" : "scale-95"
                        }`}
                    >
                        <div className="bg-background px-4 pb-4 pt-5 sm:p-6 sm:pb-4">
                            <div className="">
                                <div
                                    className="mx-auto flex size-12 shrink-0 items-center justify-center rounded-full bg-red-100 sm:mb-4"
                                >
                                    <svg
                                        className="size-6 text-red-600"
                                        fill="none"
                                        viewBox="0 0 24 24"
                                        strokeWidth="1.5"
                                        stroke="currentColor"
                                        aria-hidden="true"
                                        data-slot="icon"
                                    >
                                        <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"
                                        />
                                    </svg>
                                </div>
                                <div className="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left">
                                    <div className="mt-2">
                                        <p className="font-bold text-xl mb-2 uppercase">
                                            Use apenas o CPF do titular
                                        </p>
                                        <p>
                                            Não permitimos alteração de CPF e os saques/depósitos só são permitidos para
                                            a conta bancária do titular
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-background px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6 grid grid-cols-1">
                            <div>
                                <CustomButton onClick={action} label="Continuar" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ModalValidarDocumento;
