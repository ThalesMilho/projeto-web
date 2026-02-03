import { useRouter } from 'next/router';
import { ChevronLeft, Search } from 'lucide-react';
import { useState } from 'react';
import { loteriaModalidadesMock } from '../../../../helpers/loteriaMockData';

const Modalidade = function() {
    const router = useRouter();
    const { lotteryId, lotteryName } = router.query;
    const [searchTerm, setSearchTerm] = useState('');

    const modalidades = loteriaModalidadesMock;

    const filteredModalidades = modalidades.filter(modalidade =>
        modalidade.nome.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const handleModalidadeSelect = (modalidade) => {
        const commonQuery = {
            lotteryId,
            lotteryName,
            modalidadeId: modalidade.id,
            modalidadeNome: modalidade.nome,
            qtdDigitos: modalidade.qtdDigitosNosPalpites,
            preco: modalidade.preco,
            retorno: modalidade.retorno
        };

        if (modalidade.fluxo === 'numeros') {
            router.push({
                pathname: '/app/loteria/posicao',
                query: {
                    ...commonQuery,
                    maskDigits: modalidade.maskDigits
                }
            });
            return;
        }

        router.push({
            pathname: '/app/loteria/palpites',
            query: commonQuery
        });
    };

    return (
        <div className="min-h-screen bg-background">
            <div className="bg-degrade p-4 flex items-center justify-between text-white">
                <div className="flex items-center gap-3">
                    <button onClick={() => router.back()} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                        <ChevronLeft size={24} />
                    </button>
                    <h1 className="text-xl font-bold">MODALIDADE</h1>
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
                <div className="relative mb-4">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary" size={20} />
                    <input
                        type="text"
                        placeholder="Pesquisar..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-primary transition-colors"
                    />
                </div>

                <div className="space-y-3">
                    {filteredModalidades.map((modalidade) => (
                        <div
                            key={modalidade.id}
                            onClick={() => handleModalidadeSelect(modalidade)}
                            className="bg-white border-2 border-gray-200 rounded-xl p-4 flex items-center justify-between cursor-pointer hover:border-primary hover:shadow-lg transition-all duration-200 active:scale-98"
                        >
                            <div className="flex-1">
                                <h3 className="font-bold text-base text-primary">{modalidade.nome}</h3>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="font-bold text-primary text-lg">{modalidade.retorno}</span>
                                <ChevronLeft size={20} className="rotate-180 text-primary" />
                            </div>
                        </div>
                    ))}
                </div>

                {filteredModalidades.length === 0 && (
                    <div className="text-center py-8 text-secondary">
                        <p>Nenhuma modalidade encontrada</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Modalidade;
