import { useRouter } from 'next/router';
import { ChevronLeft } from 'lucide-react';
import { useState, useEffect } from 'react';
import { toast } from 'react-toastify';

const ValorAposta = function() {
    const router = useRouter();
    const { lotteryName, modalidadeNome, qtdDigitos, palpites } = router.query;
    
    const [valorAposta, setValorAposta] = useState('');
    const [palpitesList, setPalpitesList] = useState([]);
    const [valorPorCada, setValorPorCada] = useState(false);

    useEffect(() => {
        if (palpites) {
            try {
                setPalpitesList(JSON.parse(palpites));
            } catch (e) {
                console.error('Error parsing palpites:', e);
            }
        }
    }, [palpites]);

    const handleValorChange = (e) => {
        const value = e.target.value.replace(/[^\d,]/g, '');
        setValorAposta(value);
    };

    const handleConfirmar = () => {
        if (!valorAposta || parseFloat(valorAposta.replace(',', '.')) <= 0) {
            toast.error('Por favor, insira um valor válido', {
                position: 'top-center',
                autoClose: 2000
            });
            return;
        }

        router.push({
            pathname: '/app/loteria/selecionar-dias',
            query: {
                lotteryId: router.query.lotteryId,
                lotteryName,
                modalidadeId: router.query.modalidadeId,
                modalidadeNome,
                qtdDigitos,
                palpites: JSON.stringify(palpitesList),
                valorAposta: valorAposta,
                valorPorCada: valorPorCada
            }
        });
    };

    const valorNumerico = valorAposta ? parseFloat(valorAposta.replace(',', '.')) : 0;
    const valorTotal = valorPorCada ? (valorNumerico * palpitesList.length) : valorNumerico;

    return (
        <div className="bg-background">
            <div className="bg-degrade p-4 flex items-center justify-between text-white">
                <div className="flex items-center gap-3">
                    <button onClick={() => router.back()} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                        <ChevronLeft size={24} />
                    </button>
                    <h1 className="text-xl font-bold">VALOR DA APOSTA</h1>
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
                <div className="mb-6">
                    <h2 className="font-bold text-lg mb-2">{modalidadeNome || 'QUININHA 13D'}</h2>
                    <div className="text-sm text-secondary">
                        {palpitesList.length} palpite{palpitesList.length !== 1 ? 's' : ''} selecionado{palpitesList.length !== 1 ? 's' : ''}
                    </div>
                </div>

                <div className="bg-white rounded-2xl p-6 shadow-lg mb-6">
                    <label className="block text-sm font-semibold text-secondary mb-3">
                        Valor da aposta (R$)
                    </label>
                    <div className="relative">
                        <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-2xl font-bold text-gray-700">
                            R$
                        </span>
                        <input
                            type="text"
                            value={valorAposta}
                            onChange={handleValorChange}
                            placeholder="0,00"
                            className="w-full pl-16 pr-4 py-4 text-2xl font-bold border-2 border-gray-200 rounded-xl focus:outline-none focus:border-primary transition-colors"
                        />
                    </div>
                    <div className="mt-4">
                        <label className="flex items-center gap-3 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={valorPorCada}
                                onChange={(e) => setValorPorCada(e.target.checked)}
                                className="w-5 h-5 text-primary border-2 border-gray-300 rounded focus:ring-2 focus:ring-primary cursor-pointer"
                            />
                            <span className="text-sm font-medium text-gray-700">
                                Este valor é para <strong>CADA</strong> palpite (será multiplicado por {palpitesList.length})
                            </span>
                        </label>
                    </div>
                </div>

                {palpitesList.length > 0 && (
                    <div className="mb-6">
                        <h3 className="font-bold text-base mb-3">Resumo dos Palpites</h3>
                        <div className="space-y-2">
                            {palpitesList.map((palpite, index) => (
                                <div
                                    key={palpite.id || index}
                                    className="bg-white border-2 border-gray-200 rounded-xl p-3"
                                >
                                    {Array.isArray(palpite?.numbers) ? (
                                        <div className="flex flex-wrap gap-1">
                                            {palpite.numbers.map((num) => (
                                                <span
                                                    key={num}
                                                    className="inline-flex items-center justify-center w-8 h-8 bg-primary text-white rounded-md text-xs font-bold"
                                                >
                                                    {num.toString().padStart(2, '0')}
                                                </span>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className="flex items-center gap-2">
                                            <span className="inline-flex items-center justify-center px-3 h-8 bg-primary text-white rounded-md text-xs font-bold tracking-widest">
                                                {(palpite?.display || palpite?.value || '').toString()}
                                            </span>
                                            {palpite?.posicaoNome && (
                                                <span className="text-xs font-semibold text-secondary">
                                                    {palpite.posicaoNome}
                                                </span>
                                            )}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                <div className="bg-gradient-to-r from-primary/10 to-blue-100 rounded-2xl p-4 mb-6">
                    <div className="space-y-2">
                        {valorPorCada && valorNumerico > 0 && (
                            <div className="flex items-center justify-between text-sm text-gray-600">
                                <span>Valor por palpite:</span>
                                <span className="font-semibold">R$ {valorNumerico.toFixed(2)}</span>
                            </div>
                        )}
                        {valorPorCada && valorNumerico > 0 && (
                            <div className="flex items-center justify-between text-sm text-gray-600">
                                <span>{palpitesList.length} palpite{palpitesList.length !== 1 ? 's' : ''} × R$ {valorNumerico.toFixed(2)}</span>
                                <span></span>
                            </div>
                        )}
                        <div className="flex items-center justify-between pt-2 border-t border-primary/20">
                            <span className="font-semibold text-gray-700">Valor total da aposta:</span>
                            <span className="text-2xl font-bold text-primary">
                                R$ {valorTotal.toFixed(2)}
                            </span>
                        </div>
                    </div>
                </div>

                <button
                    onClick={handleConfirmar}
                    disabled={!valorAposta || valorNumerico <= 0}
                    className={`w-full font-bold py-4 rounded-2xl transition-all ${
                        !valorAposta || valorNumerico <= 0
                            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                            : 'bg-primary text-white hover:opacity-90 shadow-lg'
                    }`}
                >
                    Confirmar Aposta
                </button>
            </div>
        </div>
    );
};

export default ValorAposta;
