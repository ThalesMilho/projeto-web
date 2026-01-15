import { useState, useEffect } from "react";
import CustomInput1 from "@/components/CustomInput/CustomInput1";
import CustomButton from "@/components/CustomButton/CustomButton";
import SalaServiceAPI from "@/services/SalaServiceAPI";
import { Users, Trophy, DollarSign, Calendar, User } from "lucide-react";

const ModalConfiguracoesSala = function({ onClose, salaId, salaRodada, toast }) {
    const [isVisible, setIsVisible] = useState(false);
    const [rodada, setRodada] = useState(salaRodada);
    const [loading, setLoading] = useState(false);
    const salaServiceAPI = new SalaServiceAPI();
    const [salaResultado, setSalaResultado] = useState();
    const [salaInformacoesBuscadas, setSalaInformacoesBuscadas] = useState();

    useEffect(() => {
        setIsVisible(true);
        return () => {
            setIsVisible(false);
        };
    }, []);

    const onSubmit = async function(event) {
        event.preventDefault();
        setLoading(true);

        try {
            const res = await salaServiceAPI.buscarDadosRodada(rodada, salaId);
            if(res.status == 200) {
                setSalaInformacoesBuscadas(res.data.sala);
                setSalaResultado(res.data.resultado);
            } else {
                throw "Erro ao buscar dados da partida";
            }
        } catch (ex) {
            toast.error("Erro ao buscar dados da partida");
        }

        setLoading(false);
    }

    const formatCurrency = (value) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

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
                        className={`relative transform overflow-hidden rounded-lg bg-background text-left shadow-xl transition-all duration-300 sm:my-8 sm:w-full sm:max-w-4xl ${
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
                            <h2 className="text-2xl font-bold text-white mb-6">Configurações da Sala</h2>

                            <div className="mb-6">
                                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                                    <div className="sm:col-span-2">
                                        <CustomInput1
                                            required={true}
                                            value={rodada}
                                            disabled={loading}
                                            onChange={e=>setRodada(e.target.value)}
                                            type="number"
                                            label="Rodada"
                                            placeholder="Insira a rodada"
                                        />
                                    </div>
                                    <div className="flex items-end">
                                        <div onClick={onSubmit}>
                                            <CustomButton loading={loading} label="Buscar" />
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Informações da Sala */}
                            {salaInformacoesBuscadas && (
                                <div className="space-y-6">
                                    {/* Card de Informações Gerais */}
                                    <div className="bg-gray-800 rounded-lg p-5 border border-gray-700">
                                        <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                                            <Trophy className="w-5 h-5 text-yellow-500" />
                                            Informações da Sala
                                        </h3>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div className="space-y-3">
                                                <div>
                                                    <p className="text-gray-400 text-sm">Nome</p>
                                                    <p className="text-white font-medium">{salaInformacoesBuscadas.nome}</p>
                                                </div>
                                                <div>
                                                    <p className="text-gray-400 text-sm">Descrição</p>
                                                    <p className="text-white font-medium">{salaInformacoesBuscadas.descricao}</p>
                                                </div>
                                                <div>
                                                    <p className="text-gray-400 text-sm">Rodada Atual</p>
                                                    <p className="text-white font-medium flex items-center gap-2">
                                                        <Calendar className="w-4 h-4 text-blue-400" />
                                                        {salaInformacoesBuscadas.rodada}
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="space-y-3">
                                                <div>
                                                    <p className="text-gray-400 text-sm">Valor de Entrada</p>
                                                    <p className="text-green-400 font-semibold flex items-center gap-2">
                                                        <DollarSign className="w-4 h-4" />
                                                        {formatCurrency(salaInformacoesBuscadas.valor_entrada)}
                                                    </p>
                                                </div>
                                                <div>
                                                    <p className="text-gray-400 text-sm">Lucro do Vencedor (%)</p>
                                                    <p className="text-yellow-400 font-semibold">{salaInformacoesBuscadas.lucro_porcentagem}%</p>
                                                </div>
                                                <div>
                                                    <p className="text-gray-400 text-sm">Capacidade</p>
                                                    <p className="text-white font-medium flex items-center gap-2">
                                                        <Users className="w-4 h-4 text-purple-400" />
                                                        {salaInformacoesBuscadas.quantidade_jogadores} jogadores
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="mt-4 pt-4 border-t border-gray-700">
                                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                                <div>
                                                    <p className="text-gray-400 text-sm mb-1">Status</p>
                                                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                                                        salaInformacoesBuscadas.ativo ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'
                                                    }`}>
                                                        {salaInformacoesBuscadas.ativo ? 'Ativa' : 'Inativa'}
                                                    </span>
                                                </div>
                                                {salaInformacoesBuscadas.participantes && salaInformacoesBuscadas.participantes.length > 0 && (
                                                    <>
                                                        <div>
                                                            <p className="text-gray-400 text-sm mb-1">Prêmio do Vencedor</p>
                                                            <p className="text-yellow-400 font-bold text-lg flex items-center gap-1">
                                                                <Trophy className="w-4 h-4" />
                                                                {formatCurrency(
                                                                    (salaInformacoesBuscadas.participantes.length *
                                                                        salaInformacoesBuscadas.valor_entrada *
                                                                        salaInformacoesBuscadas.lucro_porcentagem) / 100
                                                                )}
                                                            </p>
                                                        </div>
                                                        <div>
                                                            <p className="text-gray-400 text-sm mb-1">Ganho do Cassino</p>
                                                            <p className="text-green-400 font-bold text-lg flex items-center gap-1">
                                                                <DollarSign className="w-4 h-4" />
                                                                {formatCurrency(
                                                                    (salaInformacoesBuscadas.participantes.length *
                                                                        salaInformacoesBuscadas.valor_entrada *
                                                                        (100 - salaInformacoesBuscadas.lucro_porcentagem)) / 100
                                                                )}
                                                            </p>
                                                        </div>
                                                    </>
                                                )}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Lista de Participantes */}
                                    <div className="bg-gray-800 rounded-lg p-5 border border-gray-700">
                                        <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                                            <Users className="w-5 h-5 text-blue-500" />
                                            Participantes ({salaInformacoesBuscadas.participantes?.length || 0})
                                        </h3>

                                        {salaInformacoesBuscadas.participantes && salaInformacoesBuscadas.participantes.length > 0 ? (
                                            <div className="space-y-3 max-h-96 overflow-y-auto">
                                                {(() => {
                                                    const participantesOrdenados = [...salaInformacoesBuscadas.participantes];
                                                    const vencedorId = salaResultado?.vencedor_id;

                                                    if (vencedorId) {
                                                        participantesOrdenados.sort((a, b) => {
                                                            if (a.user_id === vencedorId) return -1;
                                                            if (b.user_id === vencedorId) return 1;
                                                            return 0;
                                                        });
                                                    }

                                                    return participantesOrdenados.map((participante) => {
                                                        const isVencedor = participante.user_id === vencedorId;

                                                        return (
                                                            <div
                                                                key={participante.id}
                                                                className={`rounded-lg p-4 border transition-all ${
                                                                    isVencedor
                                                                        ? 'bg-gradient-to-r from-yellow-900/40 via-amber-900/40 to-yellow-900/40 border-yellow-500/50 shadow-lg shadow-yellow-500/20'
                                                                        : 'bg-gray-900/50 border-gray-700 hover:border-gray-600'
                                                                }`}
                                                            >
                                                                <div className="flex items-start justify-between">
                                                                    <div className="flex items-start gap-3 flex-1">
                                                                        <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                                                                            isVencedor
                                                                                ? 'bg-gradient-to-br from-yellow-400 to-amber-600'
                                                                                : 'bg-gradient-to-br from-blue-500 to-purple-600'
                                                                        }`}>
                                                                            {isVencedor ? (
                                                                                <Trophy className="w-5 h-5 text-white" />
                                                                            ) : (
                                                                                <User className="w-5 h-5 text-white" />
                                                                            )}
                                                                        </div>
                                                                        <div className="flex-1">
                                                                            <div className="flex items-center gap-2">
                                                                                <h4 className={`font-semibold ${isVencedor ? 'text-yellow-200' : 'text-white'}`}>
                                                                                    {participante.user.name}
                                                                                </h4>
                                                                                {isVencedor && (
                                                                                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-yellow-500 text-gray-900 animate-pulse">
                                                                                        VENCEDOR
                                                                                    </span>
                                                                                )}
                                                                            </div>
                                                                            <p className={`text-sm ${isVencedor ? 'text-yellow-300/80' : 'text-gray-400'}`}>
                                                                                {participante.user.email}
                                                                            </p>
                                                                            <div className="flex items-center gap-3 mt-2">
                                                                                <span className={`text-xs ${isVencedor ? 'text-yellow-400/70' : 'text-gray-500'}`}>
                                                                                    Tel: {participante.user.celular}
                                                                                </span>
                                                                                {participante.user.tipo === 'admin' && (
                                                                                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-900/30 text-purple-400">
                                                                                        Admin
                                                                                    </span>
                                                                                )}
                                                                                <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                                                                                    participante.user.ativo ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'
                                                                                }`}>
                                                                                    {participante.user.ativo ? 'Ativo' : 'Inativo'}
                                                                                </span>
                                                                            </div>
                                                                        </div>
                                                                    </div>
                                                                    <div className="text-right text-sm">
                                                                        <p className={isVencedor ? 'text-yellow-400/70' : 'text-gray-500'}>Entrou em</p>
                                                                        <p className={isVencedor ? 'text-yellow-200' : 'text-gray-300'}>{formatDate(participante.created_at)}</p>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        );
                                                    });
                                                })()}
                                            </div>
                                        ) : (
                                            <div className="text-center py-8 text-gray-400">
                                                <Users className="w-12 h-12 mx-auto mb-3 opacity-50" />
                                                <p>Nenhum participante nesta rodada</p>
                                            </div>
                                        )}
                                    </div>

                                    {/* Resultado */}
                                    {salaResultado && salaResultado.vencedor && (
                                        <div className="bg-gradient-to-br from-yellow-900/30 to-amber-900/30 rounded-lg p-6 border-2 border-yellow-500/50 shadow-xl shadow-yellow-500/10">
                                            <h3 className="text-2xl font-bold text-yellow-200 mb-6 flex items-center gap-3">
                                                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-yellow-400 to-amber-600 flex items-center justify-center">
                                                    <Trophy className="w-6 h-6 text-white" />
                                                </div>
                                                Vencedor da Rodada {salaResultado.rodada}
                                            </h3>
                                            <div className="bg-gray-900/50 rounded-lg p-5 border border-yellow-600/30">
                                                <div className="flex items-center gap-4">
                                                    <div className="w-16 h-16 rounded-full bg-gradient-to-br from-yellow-400 to-amber-600 flex items-center justify-center flex-shrink-0 shadow-lg">
                                                        <Trophy className="w-8 h-8 text-white" />
                                                    </div>
                                                    <div className="flex-1">
                                                        <h4 className="text-2xl font-bold text-yellow-200 mb-1">
                                                            {salaResultado.vencedor.name}
                                                        </h4>
                                                        <p className="text-yellow-300/80 mb-2">{salaResultado.vencedor.email}</p>
                                                        <div className="flex items-center gap-3">
                                                            <span className="text-sm text-yellow-400/70">
                                                                Tel: {salaResultado.vencedor.celular}
                                                            </span>
                                                            {salaResultado.vencedor.tipo === 'admin' && (
                                                                <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-purple-900/40 text-purple-300 border border-purple-500/30">
                                                                    Admin
                                                                </span>
                                                            )}
                                                        </div>
                                                    </div>
                                                    <div className="text-right">
                                                        <p className="text-yellow-400/70 text-sm mb-1">Anunciado em</p>
                                                        <p className="text-yellow-200 font-medium">{formatDate(salaResultado.created_at)}</p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            {!salaInformacoesBuscadas && !loading && (
                                <div className="text-center py-12 text-gray-400">
                                    <Trophy className="w-16 h-16 mx-auto mb-4 opacity-30" />
                                    <p className="text-lg">Digite uma rodada e clique em {'"'}Buscar{'"'} para visualizar as informações</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ModalConfiguracoesSala;