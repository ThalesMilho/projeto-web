import { useRouter } from 'next/router';
import { ChevronLeft, Coins } from 'lucide-react';
import { useMemo, useState } from 'react';
import { toast } from 'react-toastify';

const BichoValor = function() {
    const router = useRouter();

    const betValues = useMemo(
        () => [2, 5, 10, 20, 50, 100],
        []
    );

    const [selectedValue, setSelectedValue] = useState(null);

    const handleContinuar = () => {
        if (!selectedValue) {
            toast.error('Selecione um valor para continuar', {
                position: 'top-center',
                autoClose: 2000
            });
            return;
        }

        router.push({
            pathname: '/app/bicho/sorteios',
            query: {
                valorAposta: String(selectedValue)
            }
        });
    };

    return (
        <div className="bg-background min-h-screen">
            <div className="bg-degrade p-4 flex items-center justify-between text-white">
                <div className="flex items-center gap-3">
                    <button onClick={() => router.back()} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                        <ChevronLeft size={24} />
                    </button>
                    <h1 className="text-xl font-bold">JOGO DO BICHO</h1>
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

            <div className="p-4 pb-24 md:pl-64 lg:pl-72">
                <div className="mb-4">
                    <h2 className="font-bold text-xl">Escolha o valor</h2>
                    <p className="text-sm text-secondary mt-1">Selecione quanto você quer apostar</p>
                </div>

                <div className="bg-white rounded-2xl shadow-lg border-2 border-gray-200 p-4">
                    <div className="flex items-center gap-2 mb-4">
                        <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
                            <Coins size={20} />
                        </div>
                        <div>
                            <div className="font-bold text-base text-gray-900">Valores disponíveis</div>
                            <div className="text-xs text-secondary">Toque para selecionar</div>
                        </div>
                    </div>

                    <div className="grid grid-cols-3 sm:grid-cols-4 gap-3">
                        {betValues.map((v) => {
                            const isSelected = selectedValue === v;
                            return (
                                <button
                                    key={v}
                                    onClick={() => setSelectedValue(v)}
                                    className={`py-3 rounded-2xl border-2 font-bold transition-all active:scale-98 ${
                                        isSelected
                                            ? 'bg-primary text-white border-primary shadow-lg'
                                            : 'bg-white text-gray-700 border-gray-200 hover:border-primary/50'
                                    }`}
                                >
                                    R$ {v}
                                </button>
                            );
                        })}
                    </div>
                </div>

                {selectedValue && (
                    <div className="bg-gradient-to-r from-primary/10 to-blue-100 rounded-2xl p-4 mt-4">
                        <div className="flex items-center justify-between">
                            <span className="text-sm font-semibold text-gray-700">Valor selecionado</span>
                            <span className="text-2xl font-bold text-primary">R$ {selectedValue.toFixed(2)}</span>
                        </div>
                    </div>
                )}
            </div>

            <div className="fixed bottom-0 left-0 right-0 bg-white border-t-2 border-gray-200 p-4 md:pl-64 lg:pl-72">
                <button
                    onClick={handleContinuar}
                    disabled={!selectedValue}
                    className={`w-full font-bold py-4 rounded-2xl transition-all ${
                        !selectedValue
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

export default BichoValor;
