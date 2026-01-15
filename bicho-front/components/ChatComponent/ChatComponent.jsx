import CustomInput1 from "@/components/CustomInput/CustomInput1";
import CustomButton from "@/components/CustomButton/CustomButton";
import {useEffect, useRef, useState, useCallback} from "react";
import ChatServiceAPI from "@/services/ChatServiceAPI";
import CircularLoadCustom from "@/components/icons/CircularLoadCustom";
import MensagemComponent from "@/components/ChatComponent/MensagemComponent";
import moment from "moment";
import {getIdUsuarioLogado, somNotificacao, verificarUsuarioLogado} from "@/helpers/functions";
import { Volume2, VolumeX } from 'lucide-react';
import { getCookie, setCookie } from 'cookies-next';
import ModalLoginCadastro from "@/components/ModalAuth/ModalAuth";

const ChatComponent = function({ sala_id, toast, participando=false }) {

    const chatServiceAPI = new ChatServiceAPI();
    const [loading, setLoading] = useState(true);
    const [mensagens, setMensagens] = useState([]);
    const [loadingEnvio, setLoadingEnvio] = useState(false);
    const [txtMensagem, setTxtMensagem] = useState('');
    const [novasMensagens, setNovasMensagens] = useState([]);
    const [chatMuted, setChatMuted] = useState(false);
    const [showLoginModal, setShowLoginModal] = useState(false);

    const chatContainerUl = useRef();

    useEffect(() => {
        start();
        // Carrega a preferência de mute dos cookies
        const mutedPreference = getCookie('chat-muted');
        if (mutedPreference === 'true') {
            setChatMuted(true);
        }
    }, []);

    const toggleMute = () => {
        const newMutedState = !chatMuted;
        setChatMuted(newMutedState);
        // Salva a preferência nos cookies (expira em 30 dias)
        setCookie('chat-muted', newMutedState.toString(), {
            maxAge: 30 * 24 * 60 * 60, // 30 dias em segundos
            sameSite: 'lax'
        });
    };

    const scrollChatToBottom = function() {
        setTimeout(() => {
            try {
                if(chatContainerUl?.current) {
                    chatContainerUl.current.scrollTop = chatContainerUl.current.scrollHeight;
                }
            } catch (ex) {}
        }, 200);
    }

    const addMensagem = useCallback((msg_id, mensagem, user_id, user_nome, data, scroll=false) => {
        setNovasMensagens(prevNovasMensagens => {
            const jaExiste = prevNovasMensagens.some(msg => msg.id === msg_id);

            if (!jaExiste) {
                const novaMensagem = {
                    id: msg_id,
                    mensagem,
                    user: {
                        id: user_id,
                        name: user_nome
                    },
                    created_at: data,
                };

                if(scroll) {
                    scrollChatToBottom();
                }

                // Só toca o som se não estiver mutado e não for mensagem própria
                if(String(user_id) !== String(getIdUsuarioLogado()) && !chatMuted) {
                    somNotificacao();
                }

                return [...prevNovasMensagens, novaMensagem];
            }

            return prevNovasMensagens;
        });
    }, [chatMuted]);

    const novaMensagemSocket = useCallback((data) => {
        addMensagem(data.id, data.mensagem, data.user_id, data.user_nome, data.data, true);
    }, [addMensagem]);

    useEffect(() => {
        window.Echo.channel(`sala.${sala_id}`)
            .listen(".chat_nova_mensagem", novaMensagemSocket)

        return () => {
            window.Echo.leave(`sala.${sala_id}`);
        };
    }, [sala_id, novaMensagemSocket]);

    const start = async function() {
        const res = await chatServiceAPI.buscarConversasChat(sala_id);
        if(res?.status == 200) {
            setMensagens(res?.data?.data.reverse());
        }
        setLoading(false);
        scrollChatToBottom();
    }

    if(loading)
        return (
            <div className="flex justify-center">
                <CircularLoadCustom color="#fff"/>
            </div>
        );

    function getMensagensChat() {
        return [...mensagens, ...novasMensagens];
    }

    async function onSendMsg(event) {
        event.preventDefault();
        if(!verificarUsuarioLogado()) {
            setShowLoginModal(true);
            return;
        }
        if(!participando) {
            toast.error("Apenas participantes podem enviar mensagens");
            return;
        }
        if(txtMensagem.trim().length > 0) {
            setLoadingEnvio(true);
            try {
                const res = await chatServiceAPI.enviarMensagemChat(sala_id, {
                    sala_id,
                    mensagem: txtMensagem
                });
                if(res.status == 200) {
                    setLoadingEnvio(false);
                    setTxtMensagem("");
                    addMensagem(
                        res.data.id,
                        res.data.mensagem,
                        res.data.user_id,
                        res.data.name,
                        res.data.created_at,
                        true
                    );
                } else {
                    throw new Error("Error en el mensagem enviado");
                }
            } catch(err) {
                toast.error("Erro ao enviar mensagem, tente novamente");
                setLoadingEnvio(false);
            }
        }
    }

    return (
        <>
            <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-semibold text-white">Converse com os participantes</h3>
                {
                    showLoginModal ? <ModalLoginCadastro onClose={() => setShowLoginModal(false)} /> : ''
                }
                <button
                    onClick={toggleMute}
                    className={`p-2 rounded-lg transition-all duration-200 ${
                        chatMuted
                            ? 'bg-red-600 hover:bg-red-700 text-white'
                            : 'bg-gray-600 hover:bg-gray-700 text-white'
                    }`}
                    title={chatMuted ? 'Som desabilitado - Clique para habilitar' : 'Som habilitado - Clique para desabilitar'}
                >
                    {chatMuted ? (
                        <VolumeX size={18} />
                    ) : (
                        <Volume2 size={18} />
                    )}
                </button>
            </div>

            <ul ref={chatContainerUl} className="max-h-72 overflow-auto pr-2">
                {
                    getMensagensChat().map(mensagem => <MensagemComponent
                        me={String(mensagem.user.id) === String(getIdUsuarioLogado())}
                        key={mensagem.id}
                        nome={mensagem.user.name}
                        mensagem={mensagem.mensagem}
                        data={moment(mensagem.created_at).format('DD/MM/YYYY HH:mm')}
                    />)
                }
            </ul>
            <form onSubmit={onSendMsg}>
                <div className="mt-2">
                    <CustomInput1
                        textarea={true}
                        disabled={loadingEnvio}
                        value={txtMensagem}
                        onChange={(e) => setTxtMensagem(e.target.value)}
                        placeholder="Envie uma mensagem"
                    />
                </div>
                <div className="mt-2">
                    <CustomButton
                        label="Enviar"
                        bgColor="bg-success-linear"
                        loading={loadingEnvio}
                    />
                </div>
            </form>
        </>
    );
}

export default ChatComponent