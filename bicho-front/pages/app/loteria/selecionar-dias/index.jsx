import { useRouter } from 'next/router';
import { ChevronLeft, Calendar } from 'lucide-react';
import { useState, useEffect } from 'react';
import { toast } from 'react-toastify';

const SelecionarDias = function() {
    const router = useRouter();
    const { lotteryName, modalidadeNome, qtdDigitos, palpites, valorAposta, valorPorCada } = router.query;
    
    const [palpitesList, setPalpitesList] = useState([]);
    const [selectedDates, setSelectedDates] = useState([]);

    useEffect(() => {
        if (palpites) {
            try {
                setPalpitesList(JSON.parse(palpites));
            } catch (e) {
                console.error('Error parsing palpites:', e);
            }
        }
    }, [palpites]);

    const availableDates = [
        { id: 1, date: '26/01/2026', dayName: 'Hoje', time: '20:45' },
        { id: 2, date: '27/01/2026', dayName: 'Terça-feira', time: '20:45' },
        { id: 3, date: '28/01/2026', dayName: 'Quarta-feira', time: '20:45' },
        { id: 4, date: '29/01/2026', dayName: 'Quinta-feira', time: '20:45' },
        { id: 5, date: '30/01/2026', dayName: 'Sexta-feira', time: '20:45' },
        { id: 6, date: '31/01/2026', dayName: 'Sábado', time: '20:45' },
        { id: 7, date: '01/02/2026', dayName: 'Domingo', time: '20:45' },
    ];

    const handleDateToggle = (dateId) => {
        if (selectedDates.includes(dateId)) {
            setSelectedDates(selectedDates.filter(id => id !== dateId));
        } else {
            setSelectedDates([...selectedDates, dateId]);
        }
    };

    const handleContinuar = () => {
        if (selectedDates.length === 0) {
            toast.error('Por favor, selecione pelo menos uma data', {
                position: 'top-center',
                autoClose: 2000
            });
            return;
        }

        const selectedDatesData = availableDates.filter(d => selectedDates.includes(d.id));

        router.push({
            pathname: '/app/loteria/finalizar',
            query: {
                lotteryId: router.query.lotteryId,
                lotteryName,
                modalidadeId: router.query.modalidadeId,
                modalidadeNome,
                qtdDigitos,
                palpites,
                valorAposta,
                valorPorCada,
                selectedDates: JSON.stringify(selectedDatesData)
            }
        });
    };

    const valorNumerico = valorAposta ? parseFloat(valorAposta.replace(',', '.')) : 0;
    const valorPorCadaBool = valorPorCada === 'true';
    const valorBase = valorPorCadaBool ? (valorNumerico * palpitesList.length) : valorNumerico;
    const totalComDatas = valorBase * selectedDates.length;

    return (
        <div className="bg-background pb-20">
            <div className="bg-degrade p-4 flex items-center justify-between text-white">
                <div className="flex items-center gap-3">
                    <button onClick={() => router.back()} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                        <ChevronLeft size={24} />
                    </button>
                    <h1 className="text-xl font-bold">SELECIONAR DIAS</h1>
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
                <div className="bg-white rounded-2xl p-4 shadow-lg mb-4">
                    <div className="flex items-center justify-between">
                        <span className="font-semibold text-gray-700">Total</span>
                        <span className="text-2xl font-bold text-primary">
                            R$ {totalComDatas.toFixed(2)}
                        </span>
                    </div>
                </div>

                <div className="bg-white rounded-2xl shadow-lg mb-4">
                    <div className="p-4 border-b-2 border-gray-100">
                        <h2 className="font-bold text-lg">{lotteryName?.toUpperCase() || 'QUININHA'}</h2>
                    </div>

                    <div className="p-4 space-y-3">
                        {availableDates.map((dateItem) => {
                            const isSelected = selectedDates.includes(dateItem.id);
                            return (
                                <label
                                    key={dateItem.id}
                                    className={`flex items-center gap-4 p-4 rounded-xl border-2 cursor-pointer transition-all ${
                                        isSelected
                                            ? 'border-primary bg-primary/5'
                                            : 'border-gray-200 hover:border-primary/50'
                                    }`}
                                >
                                    <input
                                        type="checkbox"
                                        checked={isSelected}
                                        onChange={() => handleDateToggle(dateItem.id)}
                                        className="w-5 h-5 text-primary border-2 border-gray-300 rounded focus:ring-2 focus:ring-primary cursor-pointer"
                                    />
                                    <div className="flex-1">
                                        <div className="font-semibold text-gray-800">
                                            {dateItem.date} - {dateItem.dayName}
                                        </div>
                                        <div className="flex items-center gap-1 text-sm text-secondary mt-1">
                                            <Calendar size={14} />
                                            <span>{dateItem.time}</span>
                                        </div>
                                    </div>
                                </label>
                            );
                        })}
                    </div>
                </div>

                {selectedDates.length > 0 && (
                    <div className="bg-gradient-to-r from-primary/10 to-blue-100 rounded-2xl p-4 mb-4">
                        <div className="space-y-2">
                            <div className="flex items-center justify-between text-sm text-gray-600">
                                <span>Valor por data:</span>
                                <span className="font-semibold">R$ {valorBase.toFixed(2)}</span>
                            </div>
                            <div className="flex items-center justify-between text-sm text-gray-600">
                                <span>{selectedDates.length} data{selectedDates.length !== 1 ? 's' : ''} selecionada{selectedDates.length !== 1 ? 's' : ''}</span>
                                <span></span>
                            </div>
                            <div className="flex items-center justify-between pt-2 border-t border-primary/20">
                                <span className="font-semibold text-gray-700">Total:</span>
                                <span className="text-2xl font-bold text-primary">
                                    R$ {totalComDatas.toFixed(2)}
                                </span>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            <div className="fixed bottom-0 left-0 right-0 bg-white border-t-2 border-gray-200 p-4 md:pl-64 lg:pl-72">
                <button
                    onClick={handleContinuar}
                    disabled={selectedDates.length === 0}
                    className={`w-full font-bold py-4 rounded-2xl transition-all ${
                        selectedDates.length === 0
                            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                            : 'bg-primary text-white hover:opacity-90 shadow-lg'
                    }`}
                >
                    Continuar
                </button>
            </div>
        </div>
    );
};

export default SelecionarDias;
