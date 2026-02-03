import { useRouter } from 'next/router';
import { ChevronLeft, Trash2 } from 'lucide-react';
import { useState, useEffect } from 'react';
import { toast } from 'react-toastify';

const Palpites = function() {
    const router = useRouter();
    const { lotteryName, modalidadeNome, qtdDigitos, preco, retorno } = router.query;
    
    const [selectedNumbers, setSelectedNumbers] = useState([]);
    const [palpites, setPalpites] = useState([]);
    const totalNumbers = 80;

    const qtdDigitosNum = parseInt(qtdDigitos) || 13;

    const handleNumberClick = (number) => {
        if (selectedNumbers.includes(number)) {
            setSelectedNumbers(selectedNumbers.filter(n => n !== number));
        } else {
            if (selectedNumbers.length < qtdDigitosNum) {
                setSelectedNumbers([...selectedNumbers, number]);
            }
        }
    };

    useEffect(() => {
        if (selectedNumbers.length === qtdDigitosNum) {
            const newPalpite = {
                id: Date.now(),
                numbers: [...selectedNumbers].sort((a, b) => a - b),
                timestamp: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
            };
            setPalpites([...palpites, newPalpite]);
            setSelectedNumbers([]);
            toast.success('Palpite adicionado com sucesso!', {
                position: 'top-center',
                autoClose: 2000
            });
        }
    }, [selectedNumbers]);

    const handleDeletePalpite = (id) => {
        setPalpites(palpites.filter(p => p.id !== id));
    };

    const handleSurpresinha = () => {
        const numbers = [];
        while (numbers.length < qtdDigitosNum) {
            const random = Math.floor(Math.random() * totalNumbers) + 1;
            if (!numbers.includes(random)) {
                numbers.push(random);
            }
        }
        setSelectedNumbers(numbers);
        toast.info('Números selecionados aleatoriamente!', {
            position: 'top-center',
            autoClose: 2000
        });
    };

    const handleAvancar = () => {
        router.push({
            pathname: '/app/loteria/valor',
            query: {
                lotteryId: router.query.lotteryId,
                lotteryName,
                modalidadeId: router.query.modalidadeId,
                modalidadeNome,
                qtdDigitos,
                palpites: JSON.stringify(palpites)
            }
        });
    };

    const remainingNumbers = qtdDigitosNum - selectedNumbers.length;

    return (
        <div className=" bg-background">
            <div className="bg-degrade p-4 flex items-center justify-between text-white">
                <div className="flex items-center gap-3">
                    <button onClick={() => router.back()} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                        <ChevronLeft size={24} />
                    </button>
                    <h1 className="text-xl font-bold">{lotteryName?.toUpperCase() || 'QUININHA'}</h1>
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
                    <h2 className="font-bold text-lg">{modalidadeNome || 'QUININHA 13D'}</h2>
                    <div className="flex items-center justify-between mt-2">
                        <span className="text-red-500 font-bold">{remainingNumbers} RESTANTES</span>
                        <span className="font-bold">{palpites.length} PALPITES</span>
                    </div>
                </div>

                <div className="grid grid-cols-6 sm:grid-cols-8 md:grid-cols-9 lg:grid-cols-10 gap-1.5 sm:gap-2 mb-4">
                    {Array.from({ length: totalNumbers }, (_, i) => i + 1).map((number) => {
                        const isSelected = selectedNumbers.includes(number);
                        return (
                            <button
                                key={number}
                                onClick={() => handleNumberClick(number)}
                                className={`aspect-square rounded-lg font-bold text-xs sm:text-sm transition-all duration-200 ${
                                    isSelected
                                        ? 'bg-primary text-white shadow-lg scale-110'
                                        : 'bg-white border-2 border-gray-200 text-gray-700 hover:border-primary'
                                }`}
                            >
                                {number.toString().padStart(2, '0')}
                            </button>
                        );
                    })}
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
                <div className="flex gap-3">
                    <button
                        onClick={handleSurpresinha}
                        className="flex-1 bg-primary text-white font-bold py-4 rounded-2xl hover:opacity-90 transition-opacity"
                    >
                        Surpresinha
                    </button>
                    <button
                        onClick={handleAvancar}
                        disabled={palpites.length === 0}
                        className={`flex-1 font-bold py-4 rounded-2xl transition-opacity ${
                            palpites.length === 0
                                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                : 'bg-primary text-white hover:opacity-90'
                        }`}
                    >
                        Avançar
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Palpites;
