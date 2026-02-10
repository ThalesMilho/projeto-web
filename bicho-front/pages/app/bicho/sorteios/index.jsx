import { useRouter } from 'next/router';
import { ChevronLeft, Calendar } from 'lucide-react';
import { useMemo, useState } from 'react';
import { toast } from 'react-toastify';

const BichoSorteios = function() {
    const router = useRouter();
    const { valorAposta } = router.query;

    const availableDraws = useMemo(
        () => [
            { id: 1, date: '06/02/2026', dayName: 'Hoje', time: '11:00', nome: 'PTM - 11:00' },
            { id: 2, date: '06/02/2026', dayName: 'Hoje', time: '14:00', nome: 'PT - 14:00' },
            { id: 3, date: '06/02/2026', dayName: 'Hoje', time: '18:00', nome: 'PTV - 18:00' },
            { id: 4, date: '06/02/2026', dayName: 'Hoje', time: '21:00', nome: 'PTN - 21:00' },
            { id: 5, date: '07/02/2026', dayName: 'Sábado', time: '11:00', nome: 'Sábado - 11:00' },
            { id: 6, date: '07/02/2026', dayName: 'Sábado', time: '14:00', nome: 'Sábado - 14:00' }
        ],
        []
    );

    const [selectedDrawId, setSelectedDrawId] = useState(null);

    const handleContinuar = () => {
        const selected = availableDraws.find((d) => d.id === selectedDrawId);

        if (!selected) {
            toast.error('Selecione um sorteio para continuar', {
                position: 'top-center',
                autoClose: 2000
            });
            return;
        }

        router.push({
            pathname: '/app/bicho/animais',
            query: {
                valorAposta: valorAposta || '',
                sorteioId: String(selected.id),
                sorteioNome: selected.nome,
                sorteioDate: selected.date,
                sorteioDayName: selected.dayName,
                sorteioTime: selected.time
            }
        });
    };

    const valorNum = valorAposta ? Number(valorAposta) : 0;

    return (
        <div className="bg-background min-h-screen pb-24">
            <div className="bg-degrade p-4 flex items-center justify-between text-white">
                <div className="flex items-center gap-3">
                    <button onClick={() => router.back()} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                        <ChevronLeft size={24} />
                    </button>
                    <h1 className="text-xl font-bold">SELECIONAR SORTEIO</h1>
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

            <div className="p-4 md:pl-64 lg:pl-72">
                <div className="bg-white rounded-2xl p-4 shadow-lg mb-4 border-2 border-gray-200">
                    <div className="flex items-center justify-between">
                        <span className="font-semibold text-gray-700">Valor</span>
                        <span className="text-2xl font-bold text-primary">
                            R$ {Number.isFinite(valorNum) ? valorNum.toFixed(2) : '0.00'}
                        </span>
                    </div>
                </div>

                <div className="mb-4">
                    <h2 className="font-bold text-xl">Sorteios disponíveis</h2>
                    <p className="text-sm text-secondary mt-1">Escolha o sorteio (data e horário)</p>
                </div>

                <div className="bg-white rounded-2xl shadow-lg border-2 border-gray-200">
                    <div className="p-4 space-y-3">
                        {availableDraws.map((draw) => {
                            const isSelected = selectedDrawId === draw.id;
                            return (
                                <button
                                    key={draw.id}
                                    onClick={() => setSelectedDrawId(draw.id)}
                                    className={`w-full text-left flex items-center gap-4 p-4 rounded-xl border-2 cursor-pointer transition-all active:scale-98 ${
                                        isSelected
                                            ? 'border-primary bg-primary/5'
                                            : 'border-gray-200 hover:border-primary/50'
                                    }`}
                                >
                                    <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary flex-shrink-0">
                                        <Calendar size={18} />
                                    </div>
                                    <div className="flex-1">
                                        <div className="font-semibold text-gray-800">{draw.nome}</div>
                                        <div className="text-sm text-secondary mt-1">{draw.date} - {draw.dayName} • {draw.time}</div>
                                    </div>
                                    <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                                        isSelected ? 'border-primary' : 'border-gray-300'
                                    }`}>
                                        {isSelected && <div className="w-2.5 h-2.5 rounded-full bg-primary"></div>}
                                    </div>
                                </button>
                            );
                        })}
                    </div>
                </div>
            </div>

            <div className="fixed bottom-0 left-0 right-0 bg-white border-t-2 border-gray-200 p-4 md:pl-64 lg:pl-72">
                <button
                    onClick={handleContinuar}
                    disabled={!selectedDrawId}
                    className={`w-full font-bold py-4 rounded-2xl transition-all ${
                        !selectedDrawId
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

export default BichoSorteios;
