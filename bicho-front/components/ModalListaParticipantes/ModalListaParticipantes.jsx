import { useState, useEffect } from "react";
import { Users, Crown, Clock, User } from 'lucide-react';

const ModalListaParticipantes = function({ sala, participantes, participantesMock = [], onClose }) {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        setIsVisible(true);
        return () => {
            setIsVisible(false);
        };
    }, []);

    // Combina todos os participantes
    const getAllParticipantes = () => {
        let todosParticipantes = [];

        // Adiciona participantes fixos da sala
        if (sala?.participantes) {
            sala.participantes.forEach(p => {
                todosParticipantes.push({
                    id: p.user.id,
                    name: p.user.name,
                    tipo: 'confirmado',
                    tempo: p.created_at
                });
            });
        }

        // Adiciona participantes recentes (mock)
        participantesMock.forEach(p => {
            todosParticipantes.push({
                id: p.id,
                name: p.name,
                tipo: 'recente',
                tempo: new Date().toISOString()
            });
        });

        return todosParticipantes;
    };

    const allParticipantes = getAllParticipantes();
    const totalParticipantes = allParticipantes.length;
    const vagasRestantes = sala?.quantidade_jogadores - totalParticipantes;

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
                        {/* Botão de fechar */}
                        <button
                            type="button"
                            onClick={onClose}
                            className="absolute top-4 right-4 text-white hover:text-gray-300 focus:outline-none z-10 w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-700 transition-colors"
                            aria-label="Fechar"
                        >
                            ✖
                        </button>

                        <div className="bg-background px-6 pb-6 pt-6">
                            {/* Header */}
                            <div className="text-center mb-6">
                                <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <Users size={35} className="text-white" />
                                </div>
                                <h3 className="text-xl font-bold text-white mb-2">
                                    Lista de Participantes
                                </h3>
                            </div>

                            {/* Estatísticas */}
                            <div className="grid grid-cols-2 gap-4 mb-6">
                                <div className="bg-gray-800 rounded-lg p-3 text-center">
                                    <div className="text-blue-400 text-2xl font-bold">
                                        {totalParticipantes}
                                    </div>
                                    <div className="text-gray-300 text-xs">
                                        Participantes
                                    </div>
                                </div>

                                <div className="bg-gray-800 rounded-lg p-3 text-center">
                                    <div className="text-green-400 text-2xl font-bold">
                                        {vagasRestantes > 0 ? vagasRestantes : 0}
                                    </div>
                                    <div className="text-gray-300 text-xs">
                                        Vagas Restantes
                                    </div>
                                </div>
                            </div>

                            {/* Barra de progresso */}
                            <div className="mb-6">
                                <div className="flex justify-between text-sm text-gray-400 mb-2">
                                    <span>Progresso da sala</span>
                                    <span>{Math.round((totalParticipantes / sala?.quantidade_jogadores) * 100)}%</span>
                                </div>
                                <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
                                    <div
                                        className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full transition-all duration-1000 ease-out"
                                        style={{ width: `${(totalParticipantes / sala?.quantidade_jogadores) * 100}%` }}
                                    >
                                        <div className="h-full bg-white/20 animate-pulse"></div>
                                    </div>
                                </div>
                            </div>

                            {/* Lista de participantes */}
                            <div className="bg-gray-800 rounded-lg p-4 max-h-80 overflow-y-auto">
                                <div className="flex items-center space-x-2 mb-4">
                                    <User size={16} className="text-gray-400" />
                                    <span className="text-white font-medium text-sm">
                                        Participantes ({totalParticipantes})
                                    </span>
                                </div>

                                {allParticipantes.length > 0 ? (
                                    <div className="space-y-2">
                                        {allParticipantes.map((participante, index) => (
                                            <div
                                                key={`${participante.id}-${index}`}
                                                className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg hover:bg-gray-700 transition-colors"
                                            >
                                                <div className="flex items-center space-x-3">
                                                    <div className="relative">
                                                        {/* Avatar */}
                                                        <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                                                            <span className="text-white text-xs font-bold">
                                                                {participante.name?.charAt(0)?.toUpperCase() || 'U'}
                                                            </span>
                                                        </div>

                                                        {/* Indicador de status */}
                                                        <div className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-gray-700 ${
                                                            participante.tipo === 'confirmado' ? 'bg-green-500' : 'bg-green-500'
                                                        }`}></div>
                                                    </div>

                                                    <div>
                                                        <div className="text-white text-sm font-medium">
                                                            {participante.name}
                                                        </div>
                                                        <div className="flex items-center space-x-2">
                                                            <span className={`text-xs px-2 py-0.5 rounded-full bg-green-900/30 text-green-300`}>
                                                                Confirmado
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>

                                                <div className="text-right">
                                                    <div className="text-gray-400 text-xs">
                                                        #{index + 1}
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-center py-8">
                                        <Users size={32} className="text-gray-500 mx-auto mb-2" />
                                        <p className="text-gray-400 text-sm">
                                            Nenhum participante ainda
                                        </p>
                                        <p className="text-gray-500 text-xs">
                                            Seja o primeiro a participar!
                                        </p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ModalListaParticipantes;