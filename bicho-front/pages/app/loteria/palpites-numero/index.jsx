import { useRouter } from 'next/router';
import { ChevronLeft, Trash2 } from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';
import { toast } from 'react-toastify';

const PalpitesNumero = function() {
    const router = useRouter();
    const {
        lotteryName,
        modalidadeNome,
        qtdDigitos,
        maskDigits,
        posicaoId,
        posicaoNome
    } = router.query;

    const [inputValue, setInputValue] = useState('');
    const [currentNumbers, setCurrentNumbers] = useState([]);
    const [palpites, setPalpites] = useState([]);

    const inputRef = useRef(null);

    const qtdDigitosNum = useMemo(() => parseInt(qtdDigitos, 10) || 1, [qtdDigitos]);
    const maskDigitsNum = useMemo(() => parseInt(maskDigits, 10) || 1, [maskDigits]);

    const handleInputChange = (e) => {
        const digitsOnly = (e.target.value || '').replace(/\D/g, '');
        setInputValue(digitsOnly.slice(0, maskDigitsNum));
    };

    const handleDeletePalpite = (id) => {
        setPalpites(palpites.filter((p) => p.id !== id));
    };

    useEffect(() => {
        if (!inputValue) return;
        if (inputValue.length !== maskDigitsNum) return;

        const formatted = inputValue.padStart(maskDigitsNum, '0');

        const next = [...currentNumbers, formatted];

        if (next.length < qtdDigitosNum) {
            setCurrentNumbers(next);
        } else {
            const newPalpite = {
                id: Date.now(),
                tipo: 'numeros',
                values: next,
                display: next.join(' '),
                posicaoId: posicaoId ? parseInt(posicaoId, 10) : undefined,
                posicaoNome: posicaoNome || undefined,
                timestamp: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
            };

            setPalpites((prevPalpites) => [...prevPalpites, newPalpite]);
            setCurrentNumbers([]);

            toast.success('Palpite adicionado com sucesso!', {
                position: 'top-center',
                autoClose: 2000
            });
        }

        setInputValue('');

        setTimeout(() => {
            inputRef.current?.focus();
        }, 50);
    }, [currentNumbers, inputValue, maskDigitsNum, posicaoId, posicaoNome, qtdDigitosNum]);

    const handleAvancar = () => {
        router.push({
            pathname: '/app/loteria/valor',
            query: {
                lotteryId: router.query.lotteryId,
                lotteryName,
                modalidadeId: router.query.modalidadeId,
                modalidadeNome,
                qtdDigitos,
                maskDigits,
                posicaoId,
                posicaoNome,
                fluxo: 'numeros',
                palpites: JSON.stringify(palpites)
            }
        });
    };

    const remainingNumbers = qtdDigitosNum - currentNumbers.length;

    return (
        <div className="bg-background">
            <div className="bg-degrade p-4 flex items-center justify-between text-white">
                <div className="flex items-center gap-3">
                    <button onClick={() => router.back()} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                        <ChevronLeft size={24} />
                    </button>
                    <h1 className="text-xl font-bold">{lotteryName?.toUpperCase() || 'LOTERIA'}</h1>
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
                    <div className="flex items-center justify-between mt-2">
                        <span className="text-red-500 font-bold">{remainingNumbers} RESTANTE{remainingNumbers !== 1 ? 'S' : ''}</span>
                        <span className="font-bold">{palpites.length} PALPITE{palpites.length !== 1 ? 'S' : ''}</span>
                    </div>
                    {posicaoNome && (
                        <div className="text-sm text-secondary mt-2">
                            Posição: <span className="font-semibold text-gray-800">{posicaoNome}</span>
                        </div>
                    )}
                    {currentNumbers.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-3">
                            {currentNumbers.map((n, idx) => (
                                <span
                                    key={`${n}-${idx}`}
                                    className="inline-flex items-center justify-center px-3 py-1.5 bg-primary/10 text-primary rounded-lg text-xs font-bold tracking-widest"
                                >
                                    {n}
                                </span>
                            ))}
                        </div>
                    )}
                </div>

                <div className="bg-white rounded-2xl p-6 shadow-lg mb-6">
                    <label className="block text-sm font-semibold text-secondary mb-3">Preencha seu palpite</label>

                    <div className="flex items-center gap-3">
                        <input
                            ref={inputRef}
                            inputMode="numeric"
                            type="text"
                            value={inputValue}
                            onChange={handleInputChange}
                            placeholder={'0'.repeat(maskDigitsNum)}
                            className="flex-1 px-4 py-4 text-2xl font-bold border-2 border-gray-200 rounded-xl focus:outline-none focus:border-primary transition-colors tracking-widest"
                        />
                        <div className="text-xs text-secondary whitespace-nowrap">
                            {inputValue.length}/{maskDigitsNum}
                        </div>
                    </div>

                    <div className="mt-3 text-xs text-secondary">
                        Digite {maskDigitsNum} dígito{maskDigitsNum !== 1 ? 's' : ''} por número.
                        Ao completar {qtdDigitosNum} número{qtdDigitosNum !== 1 ? 's' : ''}, o palpite será adicionado automaticamente.
                    </div>
                </div>

                {palpites.length > 0 && (
                    <div className="mb-24">
                        <h3 className="font-bold text-base mb-3">Seus Palpites</h3>
                        <div className="space-y-2">
                            {palpites.map((palpite) => (
                                <div
                                    key={palpite.id}
                                    className="bg-white border-2 border-gray-200 rounded-xl p-3 flex items-center justify-between"
                                >
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2">
                                            <span className="inline-flex items-center justify-center px-3 py-2 bg-primary text-white rounded-lg text-sm font-bold tracking-widest">
                                                {palpite.display}
                                            </span>
                                            {palpite.posicaoNome && (
                                                <span className="text-xs font-semibold text-secondary">
                                                    {palpite.posicaoNome}
                                                </span>
                                            )}
                                        </div>
                                        <div className="text-xs text-secondary mt-1">{palpite.timestamp}</div>
                                    </div>
                                    <button
                                        onClick={() => handleDeletePalpite(palpite.id)}
                                        className="ml-3 p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                                    >
                                        <Trash2 size={18} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            <div className="fixed bottom-0 left-0 right-0 bg-white border-t-2 border-gray-200 p-4 md:pl-64 lg:pl-72">
                <button
                    onClick={handleAvancar}
                    disabled={palpites.length === 0}
                    className={`w-full font-bold py-4 rounded-2xl transition-opacity ${
                        palpites.length === 0
                            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                            : 'bg-primary text-white hover:opacity-90 shadow-lg'
                    }`}
                >
                    Avançar
                </button>
            </div>
        </div>
    );
};

export default PalpitesNumero;
