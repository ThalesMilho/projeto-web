import { useState, useEffect } from "react";
import CustomInput1 from "@/components/CustomInput/CustomInput1";
import CustomButton from "@/components/CustomButton/CustomButton";
import {toast, ToastContainer} from "react-toastify";
import SalaServiceAPI from "@/services/SalaServiceAPI";

const ModalCadastrarSala = function({ onClose }) {

    const salaServiceAPI = new SalaServiceAPI();
    const [isVisible, setIsVisible] = useState(false);
    const [loading, setLoading] = useState(false);
    const [nomeSala, setNomeSala] = useState("");
    const [linkSala, setLinkSala] = useState("");
    const [qtdPessoasSala, setQtdPessoasSala] = useState(100);
    const [valorSala, setValorSala] = useState(2);
    const [porcentagemLucro, setPorcentagemLucro] = useState(80);
    const [descricaoSala, setDescricaoSala] = useState('');

    useEffect(() => {
        setIsVisible(true);
        return () => {
            setIsVisible(false);
        };
    }, []);

    const onCadastrarSala = async function(event) {
        event.preventDefault();

        setLoading(true);
        const res = await salaServiceAPI.cadastrarSala({
            nome: nomeSala,
            descricao: descricaoSala,
            valor_entrada: parseFloat(valorSala.toString().replace(",", ".")),
            quantidade_jogadores: parseInt(qtdPessoasSala),
            lucro_porcentagem: parseInt(porcentagemLucro),
            link_da_sala: linkSala
        });

        if(res?.status === 200 || res?.status === 201) {
            onClose();
        } else {
            toast.error(res?.data?.message ?? "Ops, houve um erro ao tentar cadastrar a partida, tente novamente!");
            setLoading(false);
        }
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
                            className="absolute top-4 right-4 text-white hover:text-gray-300 focus:outline-none"
                            aria-label="Fechar"
                        >
                            ✖
                        </button>

                        <div className="bg-background px-4 pb-4 pt-5 sm:p-6 sm:pb-4">
                            <form onSubmit={onCadastrarSala}>
                                <div className="sm:flex sm:items-start">
                                    <div className="text-white font-semibold mb-4">Cadastre uma sala</div>
                                </div>
                                <div className="grid grid-cols-2 gap-3">
                                    <div className="col-span-2">
                                        <div>
                                            <CustomInput1 disabled={loading} value={linkSala}
                                                          onChange={e => setLinkSala(e.target.value)}
                                                          placeholder="Insira o link da sala" label="Link da sala"/>
                                        </div>
                                    </div>
                                    <div>
                                        <CustomInput1 disabled={loading} value={nomeSala}
                                                      onChange={e => setNomeSala(e.target.value)} required
                                                      placeholder="Insira um nome" label="Nome da sala"/>
                                    </div>
                                    <div>
                                        <CustomInput1 type="number" min={5} max={1000} disabled={loading} value={qtdPessoasSala}
                                                      onChange={e => setQtdPessoasSala(e.target.value)} required
                                                      placeholder="Insira a quantidade de pessoas" label="Limite de pessoas na sala"/>
                                    </div>
                                    <div>
                                        <CustomInput1 currency disabled={loading} value={valorSala}
                                                      onChange={e => setValorSala(e.target.value)} required
                                                      placeholder="Insira o valor da sala" label="Valor entrada R$"/>
                                    </div>
                                    <div>
                                        <CustomInput1 type="number" min={1} max={100} disabled={loading} value={porcentagemLucro}
                                                      onChange={e => setPorcentagemLucro(e.target.value)} required
                                                      placeholder="Insira a % de lucro do cliente" label="Lucro do cliente %"/>
                                    </div>
                                    <div className="col-span-2">
                                        <CustomInput1 textarea disabled={loading} value={descricaoSala}
                                                      onChange={e => setDescricaoSala(e.target.value)}
                                                      placeholder="Insira uma descrição para a sala" label="Descrição da sala"/>
                                    </div>
                                    <div className="pt-2 col-span-2">
                                        <CustomButton loading={loading} type="submit"
                                                      label="Cadastrar sala"/>
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

export default ModalCadastrarSala;
