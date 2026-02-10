import { useRouter } from 'next/router';
import { ChevronLeft } from 'lucide-react';
import { useMemo, useState } from 'react';
import { toast } from 'react-toastify';

const BichoAnimais = function() {
    const router = useRouter();
    const { valorAposta, sorteioNome, sorteioDate, sorteioDayName, sorteioTime } = router.query;

    const animals = useMemo(
        () => [
            { id: 1, numero: '01', nome: 'Avestruz', imagePath: '' },
            { id: 2, numero: '02', nome: 'Águia', imagePath: '' },
            { id: 3, numero: '03', nome: 'Burro', imagePath: '' },
            { id: 4, numero: '04', nome: 'Borboleta', imagePath: '' },
            { id: 5, numero: '05', nome: 'Cachorro', imagePath: '' },
            { id: 6, numero: '06', nome: 'Cabra', imagePath: '' },
            { id: 7, numero: '07', nome: 'Carneiro', imagePath: '' },
            { id: 8, numero: '08', nome: 'Camelo', imagePath: '' },
            { id: 9, numero: '09', nome: 'Cobra', imagePath: '' },
            { id: 10, numero: '10', nome: 'Coelho', imagePath: '' },
            { id: 11, numero: '11', nome: 'Cavalo', imagePath: '' },
            { id: 12, numero: '12', nome: 'Elefante', imagePath: '' },
            { id: 13, numero: '13', nome: 'Galo', imagePath: '' },
            { id: 14, numero: '14', nome: 'Gato', imagePath: '' },
            { id: 15, numero: '15', nome: 'Jacaré', imagePath: '' },
            { id: 16, numero: '16', nome: 'Leão', imagePath: '' },
            { id: 17, numero: '17', nome: 'Macaco', imagePath: '' },
            { id: 18, numero: '18', nome: 'Porco', imagePath: '' },
            { id: 19, numero: '19', nome: 'Pavão', imagePath: '' },
            { id: 20, numero: '20', nome: 'Peru', imagePath: '' },
            { id: 21, numero: '21', nome: 'Touro', imagePath: '' },
            { id: 22, numero: '22', nome: 'Tigre', imagePath: '' },
            { id: 23, numero: '23', nome: 'Urso', imagePath: '' },
            { id: 24, numero: '24', nome: 'Veado', imagePath: '' },
            { id: 25, numero: '25', nome: 'Vaca', imagePath: '' }
        ],
        []
    );

    const [selectedAnimalId, setSelectedAnimalId] = useState(null);

    const selectedAnimal = useMemo(
        () => animals.find((a) => a.id === selectedAnimalId) || null,
        [animals, selectedAnimalId]
    );

    const handleComprar = () => {
        if (!selectedAnimal) {
            toast.error('Selecione um animal para continuar', {
                position: 'top-center',
                autoClose: 2000
            });
            return;
        }

        toast.success('Animal selecionado! (Fluxo pronto para finalizar)', {
            position: 'top-center',
            autoClose: 2000
        });
    };

    const valorNum = valorAposta ? Number(valorAposta) : 0;

    return (
        <div className="bg-background min-h-screen pb-28">
            <div className="bg-degrade p-4 flex items-center justify-between text-white">
                <div className="flex items-center gap-3">
                    <button onClick={() => router.back()} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                        <ChevronLeft size={24} />
                    </button>
                    <h1 className="text-xl font-bold">SELECIONAR ANIMAL</h1>
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
                <div className="bg-white rounded-2xl shadow-lg border-2 border-gray-200 p-4 mb-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <div className="text-xs font-semibold text-secondary">SORTEIO</div>
                            <div className="font-bold text-gray-900">{(sorteioNome || 'Sorteio').toString()}</div>
                            <div className="text-xs text-secondary mt-1">
                                {sorteioDate ? `${sorteioDate} - ${sorteioDayName || ''}` : ''} {sorteioTime ? `• ${sorteioTime}` : ''}
                            </div>
                        </div>
                        <div className="text-right">
                            <div className="text-xs font-semibold text-secondary">VALOR</div>
                            <div className="text-xl font-bold text-primary">
                                R$ {Number.isFinite(valorNum) ? valorNum.toFixed(2) : '0.00'}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="mb-4">
                    <h2 className="font-bold text-xl">Escolha um animal</h2>
                    <p className="text-sm text-secondary mt-1">(Imagens serão adicionadas depois — já deixei o campo pronto)</p>
                </div>

                <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
                    {animals.map((a) => {
                        const isSelected = selectedAnimalId === a.id;

                        return (
                            <button
                                key={a.id}
                                onClick={() => setSelectedAnimalId(a.id)}
                                className={`bg-white border-2 rounded-2xl p-3 text-left transition-all active:scale-98 ${
                                    isSelected
                                        ? 'border-primary shadow-lg'
                                        : 'border-gray-200 hover:border-primary/50'
                                }`}
                            >
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-xs font-bold text-gray-600">{a.numero}</span>
                                    <span className={`text-[10px] font-bold px-2 py-1 rounded-full ${
                                        isSelected ? 'bg-primary text-white' : 'bg-gray-100 text-gray-600'
                                    }`}>
                                        {isSelected ? 'SELECIONADO' : 'TOQUE'}
                                    </span>
                                </div>

                                <div className="aspect-square rounded-xl bg-gray-50 border border-gray-200 flex items-center justify-center mb-2 overflow-hidden">
                                    {a.imagePath ? (
                                        <img src={a.imagePath} alt={a.nome} className="w-full h-full object-contain" />
                                    ) : (
                                        <div className="text-xs text-secondary text-center px-2">
                                            imagem aqui
                                        </div>
                                    )}
                                </div>

                                <div className="font-bold text-sm text-gray-900 leading-tight">{a.nome}</div>
                            </button>
                        );
                    })}
                </div>
            </div>

            <div className="fixed bottom-0 left-0 right-0 bg-white border-t-2 border-gray-200 p-4 md:pl-64 lg:pl-72">
                <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-semibold text-gray-700">Selecionado</span>
                    <span className="text-sm font-bold text-gray-900">
                        {selectedAnimal ? `${selectedAnimal.numero} - ${selectedAnimal.nome}` : '-'}
                    </span>
                </div>
                <button
                    onClick={handleComprar}
                    disabled={!selectedAnimal}
                    className={`w-full font-bold py-4 rounded-2xl transition-all ${
                        !selectedAnimal
                            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                            : 'bg-primary text-white hover:opacity-90 shadow-lg'
                    }`}
                >
                    Comprar
                </button>
            </div>
        </div>
    );
};

export default BichoAnimais;
