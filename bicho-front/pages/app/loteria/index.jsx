import { useRouter } from 'next/router';
import { ChevronLeft, Ticket } from 'lucide-react';
import { loteriaModalidadesMock } from '../../../helpers/loteriaMockData';

const Loteria = function() {
    const router = useRouter();

    const lotteryTypes = [
        {
            id: 1,
            nome: 'Seninha',
            foto: '/images/loteria.png'
        },
        {
            id: 2,
            nome: 'Quininha',
            foto: '/images/loteria.png'
        },
        {
            id: 3,
            nome: 'Lotinha',
            foto: '/images/loteria.png'
        },
        ...loteriaModalidadesMock
            .filter((m) => m.fluxo === 'numeros')
            .map((m) => ({
                id: m.id,
                nome: m.nome,
                foto: '/images/loteria.png',
                fluxo: 'numeros',
                modalidadeId: m.id,
                modalidadeNome: m.nome,
                qtdDigitos: m.qtdDigitosNosPalpites,
                preco: m.preco,
                retorno: m.retorno,
                maskDigits: m.maskDigits
            }))
    ];

    const handleLotterySelect = (lottery) => {
        if (lottery.fluxo === 'numeros') {
            router.push({
                pathname: '/app/loteria/posicao',
                query: {
                    lotteryId: lottery.id,
                    lotteryName: lottery.nome,
                    modalidadeId: lottery.modalidadeId,
                    modalidadeNome: lottery.modalidadeNome,
                    qtdDigitos: lottery.qtdDigitos,
                    preco: lottery.preco,
                    retorno: lottery.retorno,
                    maskDigits: lottery.maskDigits
                }
            });
            return;
        }

        router.push(`/app/loteria/modalidade?lotteryId=${lottery.id}&lotteryName=${lottery.nome}`);
    };

    return (
        <div className="min-h-screen bg-background">
            <div className="bg-degrade p-4 flex items-center gap-3 text-white">
                <button onClick={() => router.back()} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                    <ChevronLeft size={24} />
                </button>
                <h1 className="text-xl font-bold">LOTERIAS</h1>
            </div>

            <div className="p-4">
                <h2 className="font-bold text-xl mb-4">Selecione uma loteria</h2>
                
                <div className="grid grid-cols-1 gap-4">
                    {lotteryTypes.map((lottery) => (
                        <div
                            key={lottery.id}
                            onClick={() => handleLotterySelect(lottery)}
                            className="bg-white border-2 border-gray-200 rounded-2xl p-4 flex items-center gap-4 cursor-pointer hover:border-primary hover:shadow-lg transition-all duration-200 active:scale-98"
                        >
                            <div className="w-20 h-20 bg-gradient-to-br from-primary to-blue-600 rounded-xl flex items-center justify-center flex-shrink-0">
                                <Ticket size={40} className="text-white" />
                            </div>
                            <div className="flex-1">
                                <h3 className="font-bold text-lg">{lottery.nome}</h3>
                                <p className="text-sm text-secondary">Clique para ver as modalidades</p>
                            </div>
                            <div className="text-primary">
                                <ChevronLeft size={24} className="rotate-180" />
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Loteria;
