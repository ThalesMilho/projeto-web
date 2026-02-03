import { useRouter } from 'next/router';
import { ChevronLeft, Check } from 'lucide-react';
import { useState, useEffect } from 'react';
import { toast } from 'react-toastify';

const FinalizarAposta = function() {
    const router = useRouter();
    const { lotteryName, modalidadeNome, qtdDigitos, palpites, valorAposta, valorPorCada, selectedDates } = router.query;
    
    const [palpitesList, setPalpitesList] = useState([]);
    const [datesList, setDatesList] = useState([]);

    useEffect(() => {
        if (palpites) {
            try {
                setPalpitesList(JSON.parse(palpites));
            } catch (e) {
                console.error('Error parsing palpites:', e);
            }
        }
        if (selectedDates) {
            try {
                setDatesList(JSON.parse(selectedDates));
            } catch (e) {
                console.error('Error parsing dates:', e);
            }
        }
    }, [palpites, selectedDates]);

    const handleFinalizarESalvar = () => {
        const valorNumerico = valorAposta ? parseFloat(valorAposta.replace(',', '.')) : 0;
        const valorPorCadaBool = valorPorCada === 'true';
        const valorBase = valorPorCadaBool ? (valorNumerico * palpitesList.length) : valorNumerico;
        const totalFinal = valorBase * datesList.length;

        toast.success('Aposta finalizada com sucesso!', {
            position: 'top-center',
            autoClose: 3000
        });

        console.log('Aposta finalizada:', {
            loteria: lotteryName,
            modalidade: modalidadeNome,
            palpites: palpitesList,
            datas: datesList,
            valorInserido: valorAposta,
            valorPorCada: valorPorCadaBool,
            valorTotal: totalFinal
        });

        setTimeout(() => {
            router.push('/app/jogos');
        }, 1500);
    };

    const handleVoltar = () => {
        router.push('/app/jogos');
    };

    const valorNumerico = valorAposta ? parseFloat(valorAposta.replace(',', '.')) : 0;
    const valorPorCadaBool = valorPorCada === 'true';
    const valorBase = valorPorCadaBool ? (valorNumerico * palpitesList.length) : valorNumerico;
    const totalFinal = valorBase * datesList.length;

    return (
        <div className="bg-background pb-20">
            <div className="bg-degrade p-4 flex items-center justify-between text-white">
                <div className="flex items-center gap-3">
                    <button onClick={() => router.back()} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                        <ChevronLeft size={24} />
                    </button>
                    <h1 className="text-xl font-bold">FINALIZAR APOSTA</h1>
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
                <div className="bg-white rounded-2xl shadow-lg border-2 border-dashed border-primary p-6 mb-4">
                    <div className="flex items-center justify-center mb-4">
                        <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center">
                            <Check size={32} className="text-white" strokeWidth={3} />
                        </div>
                    </div>
                    <h2 className="text-center font-bold text-xl mb-2">Resumo da Aposta</h2>
                    <p className="text-center text-sm text-secondary mb-4">
                        Confira os detalhes antes de finalizar
                    </p>

                    <div className="space-y-4">
                        <div className="border-t-2 border-gray-100 pt-4">
                            <div className="text-sm font-semibold text-secondary mb-1">LOTERIA</div>
                            <div className="font-bold text-lg text-gray-800">{lotteryName?.toUpperCase() || 'QUININHA'}</div>
                        </div>

                        <div className="border-t-2 border-gray-100 pt-4">
                            <div className="text-sm font-semibold text-secondary mb-1">MODALIDADE</div>
                            <div className="font-bold text-base text-gray-800">{modalidadeNome || 'QUININHA 13D'}</div>
                        </div>

                        <div className="border-t-2 border-gray-100 pt-4">
                            <div className="text-sm font-semibold text-secondary mb-2">SORTEIOS SELECIONADOS</div>
                            <div className="space-y-2">
                                {datesList.map((dateItem, index) => (
                                    <div key={index} className="flex items-center gap-2 text-sm">
                                        <div className="w-2 h-2 bg-primary rounded-full"></div>
                                        <span className="font-medium text-primary">
                                            {dateItem.date} - {dateItem.dayName}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="border-t-2 border-gray-100 pt-4">
                            <div className="text-sm font-semibold text-secondary mb-2">MODALIDADES</div>
                            <div className="bg-gray-50 rounded-xl p-3">
                                <div className="font-semibold text-gray-800 mb-2">{modalidadeNome || 'QUININHA 19D'}</div>
                                <div className="space-y-2">
                                    {palpitesList.map((palpite, index) => (
                                        <div key={palpite.id || index}>
                                            {Array.isArray(palpite?.numbers) ? (
                                                <div className="flex flex-wrap gap-1">
                                                    {palpite.numbers.map((num) => (
                                                        <span
                                                            key={num}
                                                            className="inline-flex items-center justify-center w-7 h-7 bg-primary text-white rounded text-xs font-bold"
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
                                <div className="mt-3 pt-3 border-t border-gray-200">
                                    <div className="text-sm text-gray-600">
                                        R$ {valorAposta} {valorPorCadaBool ? '/ CADA' : '/ TOTAL'}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="border-t-2 border-primary pt-4">
                            <div className="flex items-center justify-between">
                                <span className="font-bold text-lg text-gray-700">TOTAL</span>
                                <span className="font-bold text-2xl text-primary">
                                    R$ {totalFinal.toFixed(2)}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="bg-gradient-to-r from-blue-50 to-primary/10 rounded-2xl p-4 mb-4">
                    <div className="flex items-start gap-3">
                        <div className="w-6 h-6 bg-primary rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                            <span className="text-white text-xs font-bold">i</span>
                        </div>
                        <div className="text-sm text-gray-700">
                            <p className="font-semibold mb-1">Informação importante</p>
                            <p>Ao finalizar, sua aposta será processada e o valor será debitado do seu saldo.</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="fixed bottom-0 left-0 right-0 bg-white border-t-2 border-gray-200 p-4 md:pl-64 lg:pl-72">
                <div className="flex gap-3">
                    <button
                        onClick={handleVoltar}
                        className="flex-1 bg-gray-200 text-gray-700 font-bold py-4 rounded-2xl hover:bg-gray-300 transition-colors"
                    >
                        Voltar
                    </button>
                    <button
                        onClick={handleFinalizarESalvar}
                        className="flex-1 bg-primary text-white font-bold py-4 rounded-2xl hover:opacity-90 shadow-lg transition-opacity"
                    >
                        Finalizar e Salvar
                    </button>
                </div>
            </div>
        </div>
    );
};

export default FinalizarAposta;
