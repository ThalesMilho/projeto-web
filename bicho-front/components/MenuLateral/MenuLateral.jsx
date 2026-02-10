import Image from "next/image";
import CustomButtonMenu from "@/components/CustomButton/CustomButtonMenu";
import { Trophy } from 'lucide-react';
import { DollarSign } from 'lucide-react';
import { History } from 'lucide-react';
import { Calculator } from 'lucide-react';
import { CircleUser } from 'lucide-react';
import Link from 'next/link';
import {useRouter} from "next/router";
import {useContext, useState} from "react";
import { Cable } from 'lucide-react';
import {ContextoUsuario} from "@/pages/_app";
import {usuarioStatus} from "@/models/usuario";
import { Users as UsersIcon } from 'lucide-react';
import { BarChart3 } from 'lucide-react';
import { AlertTriangle, Activity, CheckSquare, PieChart } from 'lucide-react';

const MenuLateral = function() {

    const getInitialState = function() {
        switch (router.pathname) {
            case "/app/resumo": return 1; break;
            case "/app/historico": return 2; break;
            case "/app/jogos": return 3; break;
            case "/app/financeiro": return 4; break;
            case "/app/perfil": return 5; break;
            case "/app/tipo-aposta": return 6; break;
            case "/app/usuarios": return 7; break;
            case "/app/saques": return 8; break;
            case "/app/billing": return 9; break;
            case "/app/financial-dashboard": return 10; break;
            case "/app/alerts": return 11; break;
            case "/app/transaction-approval": return 12; break;
            case "/app/game-statistics": return 13; break;
        }
    }

    const logo = require(`/public/images/logo.png`);
    const router = useRouter();
    const [active, setActive] = useState(getInitialState());
    const [dadosUsuarioLogado] = useContext(ContextoUsuario);

    return (
        <div className="fixed top-0 left-0 h-full bg-background z-10 overflow-y-auto hidden md:block md:w-64 lg:w-72 border-r-2 border-gray-200">
            <div className="p-4 h-full">
                <div className="bg-degrade rounded-3xl p-4 text-white shadow-lg">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-2xl bg-white/15 flex items-center justify-center backdrop-blur">
                            <Image src={logo} alt="Maior Bicho" width={26} height={26} />
                        </div>
                        <div className="min-w-0">
                            <div className="font-bold text-base leading-tight">Maior Bicho</div>
                            <div className="text-xs text-white/90">Menu de navegação</div>
                        </div>
                    </div>
                </div>

                <div className="mt-4 font-bold text-gray-900">Menu</div>
                <menu className="min-w-52 my-4 rounded-2xl bg-white border-2 border-gray-200 shadow-lg p-2">
                    <ul className="list-none">
                        <li className="mb-2">
                            <Link href="/app/jogos">
                                <CustomButtonMenu active={active === 3} onClick={e => setActive(3)} Icon={Trophy}
                                                  label="Jogos" className="rounded"/>
                            </Link>
                        </li>
                        {/*<li className="mb-2">*/}
                        {/*    <Link href="/app/resumo">*/}
                        {/*        <CustomButtonMenu active={active === 1} onClick={e => setActive(1)} Icon={Calculator}*/}
                        {/*                          label="Resumo" className="rounded"/>*/}
                        {/*    </Link>*/}
                        {/*</li>*/}
                        <li className="mb-2">
                            <Link href="/app/financeiro">
                                <CustomButtonMenu active={active === 4} onClick={e => setActive(4)} Icon={DollarSign}
                                                  label="Financeiro" className="rounded"/>
                            </Link>
                        </li>
                        <li className="mb-2">
                            <Link href="/app/historico">
                                <CustomButtonMenu active={active === 2} onClick={e => setActive(2)} Icon={History}
                                                  label="Histórico de apostas" className="rounded"/>
                            </Link>
                        </li>
                        <li className="mb-2">
                            <Link href="/app/perfil">
                                <CustomButtonMenu active={active === 5} onClick={e => setActive(5)} Icon={CircleUser}
                                                  label="Meu perfil" className="rounded"/>
                            </Link>
                        </li>
                    </ul>
                </menu>
                {
                    dadosUsuarioLogado?.tipo == usuarioStatus.admin && (
                        <>
                            <div className="mt-4 font-bold text-gray-900">Admin</div>
                            <menu className="min-w-52 my-4 rounded-2xl bg-white border-2 border-gray-200 shadow-lg p-2 overflow-y-auto">
                                <ul className="list-none">
                                    <li className="mb-2">
                                        <Link href="/app/usuarios">
                                            <CustomButtonMenu active={active === 7} onClick={e => setActive(7)}
                                                              Icon={UsersIcon}
                                                              label="Usuários" className="rounded"/>
                                        </Link>
                                    </li>
                                    <li className="mb-2">
                                        <Link href="/app/saques">
                                            <CustomButtonMenu active={active === 8} onClick={e => setActive(8)}
                                                              Icon={DollarSign}
                                                              label="Saques / Recargas" className="rounded"/>
                                        </Link>
                                    </li>
                                    <li className="mb-2">
                                        <Link href="/app/billing">
                                            <CustomButtonMenu active={active === 9} onClick={e => setActive(9)}
                                                              Icon={BarChart3}
                                                              label="Faturamento" className="rounded"/>
                                        </Link>
                                    </li>
                                    <li className="mb-2">
                                        <Link href="/app/financial-dashboard">
                                            <CustomButtonMenu active={active === 10} onClick={e => setActive(10)}
                                                              Icon={Activity}
                                                              label="Dashboard Financeiro" className="rounded"/>
                                        </Link>
                                    </li>
                                    <li className="mb-2">
                                        <Link href="/app/game-statistics">
                                            <CustomButtonMenu active={active === 13} onClick={e => setActive(13)}
                                                              Icon={PieChart}
                                                              label="Estatísticas de Jogos" className="rounded"/>
                                        </Link>
                                    </li>
                                    <li className="mb-2">
                                        <Link href="/app/alerts">
                                            <CustomButtonMenu active={active === 11} onClick={e => setActive(11)}
                                                              Icon={AlertTriangle}
                                                              label="Alertas de Segurança" className="rounded"/>
                                        </Link>
                                    </li>
                                    <li className="mb-2">
                                        <Link href="/app/transaction-approval">
                                            <CustomButtonMenu active={active === 12} onClick={e => setActive(12)}
                                                              Icon={CheckSquare}
                                                              label="Aprovação de Transações" className="rounded"/>
                                        </Link>
                                    </li>
                                </ul>
                            </menu>
                        </>
                    )
                }
            </div>
        </div>
    );
}

export default MenuLateral;