import { useState, useEffect } from "react";
import CustomButton from "@/components/CustomButton/CustomButton";
import {toast, ToastContainer} from "react-toastify";
import {toMoney} from "@/helpers/functions";
import { Trophy } from 'lucide-react';
import SalaServiceAPI from "@/services/SalaServiceAPI";
import {setCookie} from "cookies-next";
import {useRouter} from "next/router";

const ModalConfirmarParticipacao = function({ sala, onClose, finishParticipacao }) {
    const [isVisible, setIsVisible] = useState(false);
    const [loading, setLoading] = useState(false);
    const salaServiceAPI = new SalaServiceAPI();
    const router = useRouter();

    useEffect(() => {
        setIsVisible(true);
        return () => {
            setIsVisible(false);
        };
    }, []);

    const handleConfirmar = async function() {
        setLoading(true);
        try {
            const res = await salaServiceAPI.participar(sala.id);

            if(res?.status === 200) {
                if(finishParticipacao)
                    finishParticipacao();
                else
                    await router.push("/app/sala/"+sala.id);
            } else {
                toast.error(res?.data?.msg ? res?.data?.msg : "Ops, houve algum erro, tente novamente");
                setLoading(false);
            }

        } catch (error) {
            toast.error("Ops, houve um erro ao tentar participar do sorteio!");
            setLoading(false);
        }
    };

    const calcularPremio = () => {
        const totalArrecadado = sala.valor_entrada * sala.quantidade_jogadores;
        const premio = totalArrecadado * (sala.lucro_porcentagem / 100);
        return premio;
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
            ></div>

            <div className="fixed inset-0 z-10 w-screen overflow-y-auto">
                <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
                    <div
                        className={`relative transform overflow-hidden rounded-lg bg-background text-left shadow-xl transition-all duration-300 sm:my-8 sm:w-full sm:max-w-md ${
                            isVisible ? "scale-100" : "scale-95"
                        }`}
                    >
                        {/* Botão de fechar */}
                        <button
                            type="button"
                            onClick={onClose}
                            className="absolute top-4 right-4 text-white hover:text-gray-300 focus:outline-none z-10"
                            aria-label="Fechar"
                        >
                            ✖
                        </button>

                        <div className="bg-background px-6 pb-6 pt-6">
                            {/* Header com ícone de troféu */}
                            <div className="text-center mb-6">
                                <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <Trophy size={35} className="text-white" />
                                </div>
                                <h3 className="text-xl font-bold text-white mb-2">
                                    Confirmar Participação
                                </h3>
                                <p className="text-gray-300 text-sm">
                                    Você está prestes a participar de um sorteio incrível!
                                </p>
                            </div>

                            {/* Informações da sala */}
                            <div className="bg-gray-800 rounded-lg p-4 mb-6">
                                <div className="text-center mb-4">
                                    <div className="text-green-400 text-2xl font-bold mb-1">
                                        {toMoney(calcularPremio())}
                                    </div>
                                    <div className="text-gray-300 text-sm">
                                        Valor do prêmio
                                    </div>
                                </div>

                                <div className="space-y-3">

                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-400 text-sm">Valor para participar:</span>
                                        <span className="text-white font-bold">
                                            R$ {sala.valor_entrada.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                        </span>
                                    </div>

                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-400 text-sm">Retorno do investimento:</span>
                                        <span className="text-green-400 font-bold">
                                            {(calcularPremio() / sala.valor_entrada).toFixed(1)}x
                                        </span>
                                    </div>

                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-400 text-sm">Participantes:</span>
                                        <span className="text-white">
                                            {sala.participantes_count || 0}/{sala.quantidade_jogadores}
                                        </span>
                                    </div>

                                    {sala.descricao && (
                                        <div className="mt-3 pt-3 border-t border-gray-700">
                                            <div className="text-gray-400 text-sm mb-1">Descrição:</div>
                                            <div className="text-gray-300 text-xs">
                                                {sala.descricao}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Destacar as vantagens */}
                            <div className="bg-green-900/30 border border-green-500/30 rounded-lg p-3 mb-6">
                                <div className="flex items-start space-x-2">
                                    <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                                        <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 24 24">
                                            <path d="M9 16.17L5.53 12.7C5.14 12.31 4.51 12.31 4.12 12.7C3.73 13.09 3.73 13.72 4.12 14.11L8.41 18.41C8.8 18.8 9.43 18.8 9.82 18.41L20.18 8.05C20.57 7.66 20.57 7.03 20.18 6.64C19.79 6.25 19.16 6.25 18.77 6.64L9 16.17Z"/>
                                        </svg>
                                    </div>
                                    <div>
                                        <p className="text-green-300 text-sm font-medium">
                                            Sua chance de ganhar {(calcularPremio() / sala.valor_entrada).toFixed(1)}x mais!
                                        </p>
                                        <p className="text-green-200 text-xs mt-1">
                                            Apenas {sala.quantidade_jogadores - (sala.participantes_count || 0)} vagas restantes
                                        </p>
                                    </div>
                                </div>
                            </div>

                            {/* Botões de ação */}
                            <div>
                                <CustomButton
                                    onClick={handleConfirmar}
                                    loading={loading}
                                    label={`Participar por ${toMoney(sala.valor_entrada)}`}
                                    className="w-full"
                                />
                            </div>

                            {/* Disclaimer */}
                            <p className="text-gray-500 text-xs text-center mt-4">
                                Ao confirmar, você concorda com os termos e condições do sorteio.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ModalConfirmarParticipacao;