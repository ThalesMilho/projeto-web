import MedalhaCustom from "@/components/icons/MedalhaCustom";
import { CircleDollarSign, UsersRound, DollarSign, LogIn } from 'lucide-react';
import CustomButton from "@/components/CustomButton/CustomButton";
import {toMoney} from "@/helpers/functions";
import Link from "next/link";

const CardJogo = function({ salaId, participando, nome, valor=0, retornoPorcentagem, participantes, limiteParticipantes, onParticipar }) {

    const getValorRetorno = () => ((valor * limiteParticipantes)/100) * retornoPorcentagem;

    return (
        <Link href={(participantes == limiteParticipantes) ? '' : `/app/sala/${salaId}?enter=1`}>
            <div className={`w-full bg-tertiary shadow-xl p-4 rounded-xl border-b-4 text-white text-shadow-1 border-primary`}>
                <div className="flex justify-between items-start">
                    <div className="flex items-center -translate-y-2">
                        <MedalhaCustom size={60} />
                        <div className="pt-2 ml-4">
                            <div>Valor do prêmio</div>
                            <div className="font-bold text-4xl">{toMoney(getValorRetorno())}</div>
                        </div>
                    </div>

                    <div className="flex items-center mb-4">
                        <div className={`bg-success  box-shadow-success-1 w-3 h-3 rounded-full mr-2`}></div>
                    </div>
                </div>

                <div className="bg-background-secondary rounded-xl p-3">
                    <div className="flex justify-between mb-1">
                        <div className="flex">
                            <CircleDollarSign size={18} className="mr-2" />
                            Retorno do investimento
                        </div>
                        <span className="font-bold">{getValorRetorno() / valor}x</span>
                    </div>
                    <div className="flex justify-between mb-1">
                        <div className="flex">
                            <UsersRound size={18} className="mr-2" />
                            Qtd. de participantes
                        </div>
                        <span className="font-bold">{participantes}/{limiteParticipantes}</span>
                    </div>
                    <div className="flex justify-between">
                        <div className="flex">
                            <DollarSign size={18} className="mr-2" />
                            Valor para participar
                        </div>
                        <span className="font-bold">{toMoney(valor)}</span>
                    </div>
                </div>

                <CustomButton className="rounded-lg mt-4" label={
                    <>
                        <div className="mr-1">{participando ? "Entrar" : "Participar "+toMoney(valor)}</div>
                        {
                            participando ? <LogIn size={18} /> : ''
                        }
                    </>
                } />
            </div>
        </Link>
    );
}

export default CardJogo;