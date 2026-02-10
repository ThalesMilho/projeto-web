import { useSpring, animated } from '@react-spring/web';

const UltimoGanhador2 = function() {
    const valorFinal = 10000;

    const { valor } = useSpring({
        from: { valor: 0 },
        to: { valor: valorFinal },
        config: { tension: 100, friction: 100, duration: 800 }
    });

    return (
        <div className="min-w-[290px]">
            <animated.div className="bg-white border-2 border-gray-200 rounded-3xl overflow-hidden shadow-lg">
                <div className="p-4 bg-gradient-to-r from-primary to-blue-600 text-white">
                    <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-2xl bg-white/15 flex items-center justify-center backdrop-blur">
                            <img src="/images/coin.png" className="w-8 h-8" />
                        </div>

                        <div className="min-w-0">
                            <div className="text-xs font-semibold text-white/90">Último ganhador</div>
                            <div className="font-bold text-base leading-tight truncate">Marcos Albano</div>
                        </div>

                        <div className="ml-auto text-right">
                            <div className="text-[10px] font-bold text-white/80">Destaque</div>
                            <div className="text-xs font-bold px-3 py-1 rounded-full bg-white/15">Hoje</div>
                        </div>
                    </div>
                </div>

                <div className="p-4">
                    <div className="flex items-center justify-between">
                        <div className="text-xs font-bold text-success-dark">Últimos ganhadores</div>
                        <div className="text-[10px] font-semibold text-secondary">Atualizado agora</div>
                    </div>

                    <div className="mt-3 space-y-1 text-sm text-gray-700">
                        <div className="flex items-center justify-between gap-3">
                            <span className="text-secondary font-semibold">Data</span>
                            <span className="font-bold">28/11/2025 14:26</span>
                        </div>
                        <div className="flex items-center justify-between gap-3">
                            <span className="text-secondary font-semibold">Unidade</span>
                            <span className="font-bold">423432</span>
                        </div>
                        <div className="flex items-center justify-between gap-3">
                            <span className="text-secondary font-semibold">Aposta</span>
                            <span className="font-bold">R$ 20,00</span>
                        </div>
                    </div>

                    <div className="mt-3 pt-3 border-t border-gray-100">
                        <div className="text-xs font-semibold text-secondary text-center">Prêmio</div>
                        <animated.p className="font-black text-primary text-center text-4xl mt-1 whitespace-nowrap">
                            {valor.to(v => `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`)}
                        </animated.p>
                    </div>
                </div>
            </animated.div>
        </div>
    )
}

export default UltimoGanhador2;