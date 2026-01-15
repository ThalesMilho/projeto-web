import { useSpring, animated } from '@react-spring/web';

const UltimoGanhador = function() {
    const valorFinal = 10000;

    const { valor } = useSpring({
        from: { valor: 0 },
        to: { valor: valorFinal },
        config: { tension: 100, friction: 100, duration: 1500 }
    });

    return (
        <div className="drop-shadow-lg">
            <div className="bg-degrade rounded-3xl p-4 pb-2">
                <div className="bg-white text-success-dark rounded-full px-4 py-1 font-semibold w-52 text-center relative mx-auto -translate-x-6">
                    <span>Ultimo ganhador</span>
                    <img src="/images/coin.png" className="w-12 absolute -right-16 -top-10" />
                </div>
                <animated.p className="font-black text-white text-center text-4xl mt-4">
                    {valor.to(v => `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`)}
                </animated.p>
            </div>
        </div>
    )
}

export default UltimoGanhador