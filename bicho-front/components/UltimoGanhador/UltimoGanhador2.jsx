import { useSpring, animated } from '@react-spring/web';

const UltimoGanhador2 = function() {
    const valorFinal = 10000;

    const { valor } = useSpring({
        from: { valor: 0 },
        to: { valor: valorFinal },
        config: { tension: 100, friction: 100, duration: 800 }
    });

    return (
        <div className="">
            <animated.div className="border transition-all border-primary border-2 rounded-3xl overflow-hidden">
                <div className="p-4 py-3 bg-degrade text-white">
                    <div className="flex whitespace-nowrap">
                        <div className="mr-4">
                            <img src="/images/coin.png" className="w-12 min-w-12" />
                        </div>

                        <div>
                            <div className=" font-bold">Último ganhador</div>
                            <div className="">Marcos Albano</div>
                        </div>
                    </div>
                </div>
                <div className="p-4 pt-2">
                    <div className="text-success-dark flex justify-between">
                        <div className="py-1 rounded-full mr-4">
                            <span className="whitespace-nowrap font-bold">Ultimos ganhadores</span>
                        </div>
                    </div>
                    <div>
                        <p><b>Data: </b> 28/11/2025 14:26</p>
                        <p><b>Unidade:</b> 423432</p>
                        <p><b>Pagou :</b> R$20,00 e ganhou</p>
                    </div>
                    <animated.p className="font-black text-primary text-center text-4xl mt-2 whitespace-nowrap">
                        {valor.to(v => `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`)}
                    </animated.p>
                </div>
            </animated.div>
        </div>
    )
}

export default UltimoGanhador2;