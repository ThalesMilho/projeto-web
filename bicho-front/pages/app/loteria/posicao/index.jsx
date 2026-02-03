import { useRouter } from 'next/router';
import { ChevronLeft } from 'lucide-react';
import { loteriaPosicoesMock } from '../../../../helpers/loteriaMockData';

const Posicao = function() {
    const router = useRouter();
    const { lotteryId, lotteryName, modalidadeId, modalidadeNome, qtdDigitos, preco, retorno, maskDigits } = router.query;

    const handlePosicaoSelect = (posicao) => {
        router.push({
            pathname: '/app/loteria/palpites-numero',
            query: {
                lotteryId,
                lotteryName,
                modalidadeId,
                modalidadeNome,
                qtdDigitos,
                preco,
                retorno,
                maskDigits,
                posicaoId: posicao.id,
                posicaoNome: posicao.nome,
                fluxo: 'numeros'
            }
        });
    };

    return (
        <div className="min-h-screen bg-background">
            <div className="bg-degrade p-4 flex items-center justify-between text-white">
                <div className="flex items-center gap-3">
                    <button onClick={() => router.back()} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                        <ChevronLeft size={24} />
                    </button>
                    <h1 className="text-xl font-bold">POSIÇÃO</h1>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                    <span className="font-semibold">R$ *****.**</span>
                    <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                            <circle cx="12" cy="12" r="3"></circle>
                        </svg>
                    </button>
                </div>
            </div>

            <div className="p-4">
                <div className="mb-4">
                    <h2 className="font-bold text-lg">{modalidadeNome || 'CENTENA'}</h2>
                    <p className="text-sm text-secondary mt-1">Escolha a posição do prêmio</p>
                </div>

                <div className="space-y-3">
                    {loteriaPosicoesMock.map((posicao) => (
                        <div
                            key={posicao.id}
                            onClick={() => handlePosicaoSelect(posicao)}
                            className="bg-white border-2 border-gray-200 rounded-xl p-4 flex items-center justify-between cursor-pointer hover:border-primary hover:shadow-lg transition-all duration-200 active:scale-98"
                        >
                            <div className="flex-1">
                                <h3 className="font-bold text-base text-primary">{posicao.nome}</h3>
                            </div>
                            <div className="text-primary">
                                <ChevronLeft size={20} className="rotate-180" />
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Posicao;
