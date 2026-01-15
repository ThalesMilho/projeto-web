import {useState, useEffect, useCallback, useContext} from "react";
import {toMoney, verificarUsuarioLogado} from "@/helpers/functions";
import CircularLoadCustom from "@/components/icons/CircularLoadCustom";
import {EyeIcon, SettingsIcon, Trophy} from 'lucide-react';
import CustomButton from "@/components/CustomButton/CustomButton";
import Link from "next/link";
import CustomInput1 from "@/components/CustomInput/CustomInput1";
import ChatComponent from "@/components/ChatComponent/ChatComponent";
import {toast, ToastContainer} from "react-toastify";
import ModalConfirmarParticipacao from "@/components/ModalConfirmarParticipacao/ModalConfirmarParticipacao";
import ModalLoginCadastro from "@/components/ModalAuth/ModalAuth";
import {CopyToClipboard} from "react-copy-to-clipboard/src";
import ModalListaParticipantes from "@/components/ModalListaParticipantes/ModalListaParticipantes";
import {usuarioStatus} from "@/models/usuario";
import {ContextoUsuario} from "@/pages/_app";
import ModalConfiguracoesSala from "@/components/ModalConfiguracoesSala/ModalConfiguracoesSala";
import ModalRealizarRecargaFull from "@/components/ModalRealizarRecargaFull/ModalRealizarRecargaFull";
import {useRouter} from "next/router";
import Tabs from "@/components/Tabs/Tabs";
import moment from "moment";

const SalaEspera = function({ salaInformacoes }) {
    const [mostrarSorteio, setMostrarSorteio] = useState(false);
    const [vencedor, setVencedor] = useState("");
    const [animacaoTexto, setAnimacaoTexto] = useState("");
    const [participantesMock, setParticipantesMock] = useState([]);
    const [showModalConfirmarParticipacao, setShowModalConfirmarParticipacao] = useState(false);
    const [showModalLogin, setShowModalLogin] = useState(false);
    const [showModalParticipantes, setShowModalParticipantes] = useState(false);
    const [showModalConfiguracoes, setShowModalConfiguracoes] = useState(false);
    const [showModalRecarga, setShowModalRecarga] = useState(false);
    const [dadosUsuarioLogado] = useContext(ContextoUsuario);
    const router = useRouter();

    const iniciarSorteio = useCallback((data) => {
        setMostrarSorteio(true);

        let contador = 0;
        let contadorIndex = 0;
        const maxTrocas = 20;

        const animacao = setInterval(() => {
            const infoParticipantes = getInfoParticipantes();
            let participanteAleatorio = infoParticipantes[contadorIndex];

            if(!participanteAleatorio) {
                participanteAleatorio = infoParticipantes[0];
                contadorIndex = 0;
            }

            setAnimacaoTexto(participanteAleatorio?.name ?? "Sorteando...");
            contador++;
            contadorIndex++;

            if (contador >= maxTrocas) {
                clearInterval(animacao);
                setVencedor(data.usuario_vencedor);
                setAnimacaoTexto("");
            }
        }, 200);
    }, [participantesMock]);

    const atualizarParticipantesRecentes = useCallback((data) => {
        if(data.participante) {
            setParticipantesMock(prevParticipantes => {
                // Verifica se já existe usando o estado atual
                const jaExiste = prevParticipantes.some(p => p.id === data.participante_id);

                // Também verifica nos participantes fixos da sala
                const existeNaSala = salaInformacoes.participantes.some(p =>
                    p.user.id === data.participante_id
                );

                if (!jaExiste && !existeNaSala) {
                    return [
                        ...prevParticipantes,
                        { id: data.participante_id, name: data.participante }
                    ];
                }

                return prevParticipantes;
            });
        }
    }, [salaInformacoes.participantes]); // Adicionada dependência necessária

    useEffect(() => {
        if(dadosUsuarioLogado) {
            if(!dadosUsuarioLogado.saldo || parseFloat(dadosUsuarioLogado.saldo) < salaInformacoes?.valor_entrada) {
                setTimeout(() => setShowModalRecarga(true), 500)
            } else {
                setTimeout(() => setShowModalConfirmarParticipacao(true), 500)
            }
        } else {
            setTimeout(() => setShowModalLogin(true), 500)
        }
    }, []);

    useEffect(() => {
        if(salaInformacoes?.id) {
            window.Echo.channel(`sala.${salaInformacoes.id}`)
                .listen(".novo_participante", atualizarParticipantesRecentes)
                .listen(".sala_sorteada", iniciarSorteio);
        }

        return () => {
            if(salaInformacoes?.id) {
                window.Echo.leave(`sala.${salaInformacoes.id}`);
            }
        };
    }, [salaInformacoes?.id, atualizarParticipantesRecentes, iniciarSorteio]);

    const getInfoParticipantes = function() {
        let tmp = [];
        salaInformacoes.participantes.forEach(p => {
            tmp.push(p.user);
        });
        return [...tmp, ...participantesMock];
    }

    const calcularQtdJogadoresNaSala = () => {
        return salaInformacoes.participantes_count + participantesMock.length;
    }

    const calcularPremio = () => {
        return salaInformacoes.valor_entrada * salaInformacoes.quantidade_jogadores * (salaInformacoes.lucro_porcentagem / 100);
    };

    const porcentagemPreenchimento = (calcularQtdJogadoresNaSala() / salaInformacoes.quantidade_jogadores) * 100;
    const getValorRetorno = () => ((salaInformacoes.valor_entrada * salaInformacoes.quantidade_jogadores)/100) * salaInformacoes.lucro_porcentagem;

    if (mostrarSorteio) {
        return (
            <div className="min-h-[60vh] w-full flex flex-col items-center justify-center">
                {vencedor ? (
                    // Resultado do sorteio
                    <div className="text-center w-full">
                        <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
                            <Trophy size={35} className="text-white" />
                        </div>

                        <div className="text-2xl font-bold text-yellow-400 mb-4 animate-bounce">
                            🎉 PARABÉNS! 🎉
                        </div>

                        <div className="text-xl text-white font-bold mb-2">
                            Vencedor: {vencedor}
                        </div>

                        <div className="text-xl text-green-400 font-bold mb-6">
                            Prêmio: {toMoney(calcularPremio())}
                        </div>

                        <div className="mb-3 bg-background-tertiary rounded-2xl p-6 w-full mx-auto">
                            <div className="text-gray-300 text-sm mb-4">
                                Detalhes do sorteio:
                            </div>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Total participantes:</span>
                                    <span className="text-white">{salaInformacoes.quantidade_jogadores}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Valor por entrada:</span>
                                    <span className="text-white">{toMoney(salaInformacoes.valor_entrada)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Premiação:</span>
                                    <span className="text-white">{toMoney(getValorRetorno())}</span>
                                </div>
                            </div>
                        </div>

                        <CustomButton label="Voltar" onClick={() => window.location.reload()} />

                    </div>
                ) : (
                    // Animação do sorteio
                    <div className="text-center">
                        <div className="text-xl font-bold text-white mb-8">
                            🎲 SORTEANDO... 🎲
                        </div>

                        <div className="bg-background-tertiary rounded-2xl p-8 mb-6 min-h-[120px] flex items-center justify-center">
                            <div className="text-2xl font-bold text-success animate-pulse">
                                {animacaoTexto || "..."}
                            </div>
                        </div>

                        <div className="text-gray-300">
                            Sorteando entre {salaInformacoes.quantidade_jogadores} participantes...
                        </div>
                    </div>
                )}
            </div>
        );
    }

    const onParticipar = function() {
        if(verificarUsuarioLogado()) {
            if(!dadosUsuarioLogado.saldo || parseFloat(dadosUsuarioLogado.saldo) < salaInformacoes?.valor_entrada)
                setShowModalRecarga(true);
            else
                setShowModalConfirmarParticipacao(true);
        } else {
            setShowModalLogin(true)
        }
    }

    const finishParticipacao = function() {
        window.location.reload();
    }

    const copiadoComSucesso = function () {
        toast.success("Link copiado com sucesso!");
    };

    return (
        <div className="text-white">
            <ToastContainer />
            {
                showModalLogin ? <ModalLoginCadastro onClose={() => setShowModalLogin(false)} /> : ''
            }
            {/* Header da sala */}
            <div className="grid gap-5">
                <div className="">
                    <div className="mb-4">
                        <h2 className="font-bold text-white text-center">{salaInformacoes.nome}</h2>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        <div className="bg-success-linear rounded-2xl p-4 text-center relative overflow-hidden">
                            <img src="/images/wave_1.svg" className="absolute right-0 bottom-0 h-[70%]" style={{ zIndex: 1 }} />
                            <div style={{ zIndex:2 }} className="text-sm">Prêmio Total</div>
                            <div style={{ zIndex:2 }} className="text-2xl font-bold text-white text-shadow-1 relative">
                                {toMoney(calcularPremio())}
                            </div>
                        </div>

                        <div className="bg-success-linear rounded-2xl p-4 text-center relative overflow-hidden">
                            <img src="/images/wave_1.svg" className="absolute right-0 bottom-0 h-[70%]" style={{ zIndex: 1 }} />
                            <div style={{ zIndex:2 }} className="text-sm">Retorno</div>
                            <div style={{ zIndex:2 }} className="text-2xl font-bold text-white text-shadow-1 relative">
                                {(calcularPremio() / salaInformacoes.valor_entrada).toFixed(1)}x
                                {/*{salaInformacoes.lucro_porcentagem}x*/}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Mensagem de espera */}
                {salaInformacoes.participantes_count < salaInformacoes.quantidade_jogadores && (
                    <div className="bg-[#101724] border border-border rounded-2xl overflow-hidden relative">
                        <img src="/images/quadradoBackground.png" className="absolute right-0 top-0" style={{ height: '100%', maxHeight: 200 }}/>
                        <div className="p-4">
                            <div className="flex items-center space-x-3">
                                <CopyToClipboard onCopy={copiadoComSucesso} text={`https://salapix.com.br/${salaInformacoes?.path ? salaInformacoes?.path : ("app/sala/"+salaInformacoes.id)}`}>
                                    <div>
                                        <div className="text-blue-100 mb-1 font-bold">Aguarde mais participantes...</div>
                                        <div className="text-blue-100 text-sm underline uppercase">
                                            Convide os seus amigos
                                        </div>
                                        {/*<div className="cursor-pointer w-fit text-blue-400 font-medium">https://salapix.com.br/{salaInformacoes?.path ? salaInformacoes?.path : ("app/sala/"+salaInformacoes.id)}</div>*/}
                                    </div>
                                </CopyToClipboard>
                            </div>
                        </div>
                    </div>
                )}

                <div className="rounded-2xl">
                    <div className="flex items-center mb-2">
                        <img src="/images/double_people.svg" className="w-8 mr-2"/>
                        <div>
                            <p>Participantes</p>
                            <p className="font-bold text-xl">{calcularQtdJogadoresNaSala()}/{salaInformacoes.quantidade_jogadores}</p>
                        </div>
                    </div>

                    {/* Barra de progresso animada */}
                    <div className="w-full bg-gray-700 rounded-full h-2 mb-4">
                        <div
                            className="bg-primary h-2 rounded-full transition-all duration-1000 ease-out relative"
                            style={{ width: `${porcentagemPreenchimento}%`, boxShadow: '0px 0px 5px 2px #3CE094' }}
                        >
                            <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
                        </div>
                    </div>

                    <div className="flex justify-between text-sm">
                        <span className="text-gray-400">
                            Faltam {salaInformacoes.quantidade_jogadores - calcularQtdJogadoresNaSala()} participantes
                        </span>
                        <span className="text-gray-400 text-end">
                            {calcularQtdJogadoresNaSala() >= salaInformacoes.quantidade_jogadores ?
                                "Sala lotada! Sorteio em breve..." :
                                `${porcentagemPreenchimento.toFixed(0)}% preenchido`
                            }
                        </span>
                    </div>
                </div>

                {
                    !salaInformacoes?.participando_count ? (
                        <>
                            {
                                showModalConfirmarParticipacao ? <ModalConfirmarParticipacao finishParticipacao={finishParticipacao} sala={salaInformacoes} onClose={() => setShowModalConfirmarParticipacao(false)} /> : ''
                            }
                            <button onClick={onParticipar} className="rounded-full w-full bg-success-linear text-white p-4 text-center hover:animate-none hover:scale-105 transition-transform shadow-lg hover:shadow-xl relative overflow-hidden before:absolute before:inset-0 before:bg-gradient-to-r before:from-transparent before:via-white/30 before:to-transparent before:translate-x-[-100%] before:animate-[shine_2s_infinite] before:skew-x-12">
                                Clique aqui para participar
                            </button>
                        </>
                    ) : ''
                }

                <Tabs
                    tabs={[{
                        titulo: 'Participantes',
                        render: <ul>
                            {salaInformacoes?.participantes?.map((participante,index) => (
                                <li key={index}>
                                    <div className="flex items-center p-4">
                                        <img src="/images/profile.svg" className="w-11 mr-3" />
                                        <div>
                                            <p className="font-semibold">{participante.user.name}</p>
                                            <p className="font-light">{moment(participante.created_at).format('DD/MM/YYYY HH:mm:ss')}</p>
                                        </div>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    },
                    {
                        titulo: 'Chat aberto',
                        render: (<div className="p-4">
                            <ChatComponent sala_id={salaInformacoes.id} participando={salaInformacoes?.participando_count} toast={toast} />
                        </div>)
                    }]}
                />

                {
                    (salaInformacoes?.participando_count && dadosUsuarioLogado?.tipo != usuarioStatus.admin) ? (
                        <>
                            {
                                showModalParticipantes ?
                                    <ModalListaParticipantes sala={salaInformacoes} participantesMock={participantesMock} onClose={() => setShowModalParticipantes(false)} />
                                    :
                                    ''
                            }
                            <button onClick={() => setShowModalParticipantes(true)} className="flex justify-center items-center h-24 w-full bg-purple-800 font-bold text-white rounded-2xl p-4 text-center hover:animate-none hover:scale-105 transition-transform shadow-lg hover:shadow-xl relative overflow-hidden before:absolute before:inset-0 before:bg-gradient-to-r before:from-transparent before:via-white/30 before:to-transparent before:translate-x-[-100%] before:animate-[shine_2s_infinite] before:skew-x-12">
                                <div className="mr-2">
                                    <EyeIcon />
                                </div>
                                Ver participantes
                            </button>
                        </>
                    ) : ''
                }

                {
                    showModalRecarga ? <ModalRealizarRecargaFull onClose={() => setShowModalRecarga(false)} /> : ''
                }

                {
                    dadosUsuarioLogado?.tipo == usuarioStatus.admin ? (
                        <>
                            {
                                showModalParticipantes ?
                                    <ModalListaParticipantes sala={salaInformacoes} participantesMock={participantesMock} onClose={() => setShowModalParticipantes(false)} />
                                    :
                                    ''
                            }
                            {
                                showModalConfiguracoes ?
                                    <ModalConfiguracoesSala toast={toast} salaId={salaInformacoes.id} salaRodada={salaInformacoes.rodada} onClose={() => setShowModalConfiguracoes(false)} />
                                    :
                                    ''
                            }
                            <div className="grid grid-cols-2 gap-4">
                                <button onClick={() => setShowModalParticipantes(true)} className="flex justify-center items-center h-24 w-full bg-purple-800 font-bold text-white rounded-2xl p-4 text-center hover:animate-none hover:scale-105 transition-transform shadow-lg hover:shadow-xl relative overflow-hidden before:absolute before:inset-0 before:bg-gradient-to-r before:from-transparent before:via-white/30 before:to-transparent before:translate-x-[-100%] before:animate-[shine_2s_infinite] before:skew-x-12">
                                    <div className="mr-2">
                                        <EyeIcon />
                                    </div>
                                    Ver participantes
                                </button>

                                <button onClick={() => setShowModalConfiguracoes(true)} className="flex justify-center items-center h-24 w-full bg-orange-500 font-bold text-white rounded-2xl p-4 text-center hover:animate-none hover:scale-105 transition-transform shadow-lg hover:shadow-xl relative overflow-hidden before:absolute before:inset-0 before:bg-gradient-to-r before:from-transparent before:via-white/30 before:to-transparent before:translate-x-[-100%] before:animate-[shine_2s_infinite] before:skew-x-12">
                                    <div className="mr-2">
                                        <SettingsIcon />
                                    </div>
                                    Configurações
                                </button>
                            </div>
                        </>
                    ) : ''
                }


                {/* Informações adicionais */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Suas chances */}
                    <div className="bg-background-tertiary rounded-2xl p-6 h-min">
                        <h3 className="text-lg font-semibold text-white mb-4">Suas Chances</h3>
                        <div className="space-y-3">
                            <div className="flex justify-between">
                                <span className="text-gray-400">Seu investimento:</span>
                                <span className="text-white font-bold">{toMoney(salaInformacoes.valor_entrada)}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-400">Possível retorno:</span>
                                <span className="text-green-400 font-bold">{toMoney(calcularPremio())}</span>
                            </div>
                        </div>
                    </div>

                    {/* Últimos participantes */}
                    <div className="bg-background-tertiary rounded-2xl p-6">
                        <ChatComponent sala_id={salaInformacoes.id} participando={salaInformacoes?.participando_count} toast={toast} />
                        <h3 className="text-lg font-semibold text-white mt-4 mb-2">Participantes Recentes</h3>
                        <div className="space-y-2 overflow-y-auto">
                            {getInfoParticipantes().map((particip, index) => (
                                <div key={index} className="flex items-center space-x-2">
                                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                    <span className="text-gray-300 text-sm">{particip.name}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SalaEspera;