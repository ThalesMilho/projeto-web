import ClockCustom from "@/components/icons/ClockCustom";
import BotaoMenuInferior from "@/components/MenuInferior/BotaoMenuInferior";
import {useEffect, useState} from "react";
import Link from "next/link";
import {useRouter} from "next/router";
import TicketCustom from "@/components/icons/TicketCustom";
import FutbolCustom from "@/components/icons/FutbolCustom";
import DollarCustom from "@/components/icons/DollarCustom";
import UserCustom from "@/components/icons/UserCustom";
import PixCustom from "@/components/icons/PixCustom";

const MenuInferior = function() {

    const getInitialState = function() {
        switch (router.pathname) {
            case "/app/resumo": return 1; break;
            case "/app/historico": return 2; break;
            case "/app/jogos": return 3; break;
            case "/app/financeiro": return 4; break;
            case "/app/perfil": return 5; break;
        }
    }

    const router = useRouter();
    const [active, setActive] = useState(getInitialState());


    return (
        <div className="w-full bg-primary h-17 fixed bottom-0 -box-shadow-menu-y lg:hidden" style={{ minHeight: '84px' }}>
            <div className="grid grid-cols-4 h-full">
                {/*<Link href="/app/resumo" className="flex justify-center items-center w-full">*/}
                {/*    <BotaoMenuInferior setActive={setActive} index={1} active={active === 1} Icon={TicketCustom} />*/}
                {/*</Link>*/}
                <Link href="/app/historico" className="flex justify-center items-center w-full">
                    <BotaoMenuInferior setActive={setActive} index={2} active={active === 2} Icon={ClockCustom} />
                </Link>
                <Link href="/app/jogos" className="flex justify-center items-center w-full">
                    <BotaoMenuInferior setActive={setActive} index={3} active={active === 3} Icon={PixCustom} />
                </Link>
                <Link href="/app/financeiro" className="flex justify-center items-center w-full">
                    <BotaoMenuInferior setActive={setActive} index={4} active={active === 4 || window.location.pathname === "/app/billing"} Icon={DollarCustom} />
                </Link>
                <Link href="/app/perfil" className="flex justify-center items-center w-full">
                    <BotaoMenuInferior setActive={setActive} index={5} active={active === 5} Icon={UserCustom} />
                </Link>
            </div>
        </div>
    );
}

export default MenuInferior;