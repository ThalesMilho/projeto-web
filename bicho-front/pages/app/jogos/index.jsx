import UltimoGanhador from "@/components/UltimoGanhador/UltimoGanhador";
import { DollarSign } from 'lucide-react';
import UltimoGanhador2 from "@/components/UltimoGanhador/UltimoGanhador2";
import { useRouter } from 'next/router';

const Home = function() {
    const router = useRouter();

    return (
        <div className="min-h-screen bg-background">

            <div className="p-4 md:pl-64 lg:pl-72">
                <div>
                    <div className="flex items-center justify-between">
                        <div>
                            <div className="font-bold text-xl text-gray-900">Últimos ganhadores</div>
                            <div className="text-sm text-secondary mt-1">Acompanhe os maiores prêmios</div>
                        </div>
                        <div className="text-xs font-bold px-3 py-2 rounded-xl bg-primary/10 text-primary">
                            Atualizando
                        </div>
                    </div>

                    <div className="-mx-4 mt-4">
                        <div className="px-4 flex gap-4 overflow-x-auto hide-scrollbar pb-1">
                            <UltimoGanhador2 />
                            <UltimoGanhador2 />
                            <UltimoGanhador2 />
                            <UltimoGanhador2 />
                        </div>
                    </div>
                </div>

                <div className="mt-4">
                    <div className="flex items-end justify-between gap-3">
                        <div>
                            <h3 className="font-bold text-xl text-gray-900">Selecione um jogo</h3>
                            <p className="text-sm text-secondary mt-1">Escolha uma opção para começar</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-3">
                        <button
                            type="button"
                            onClick={() => router.push('/app/bicho')}
                            className="group text-left bg-white border-2 border-gray-200 rounded-3xl overflow-hidden shadow-lg hover:border-primary/50 hover:shadow-xl transition-all active:scale-[0.99]"
                        >
                            <div className="relative">
                                <img className="w-full h-44 object-cover" src="/images/bicho.png" />
                                <div className="absolute inset-0 bg-gradient-to-t from-black/55 via-black/10 to-transparent"></div>
                                <div className="absolute bottom-3 left-3 right-3">
                                    <div className="flex items-center justify-between gap-3">
                                        <div>
                                            <div className="text-white font-bold text-lg">Jogo do bicho</div>
                                            <div className="text-white/90 text-xs">Valores, sorteio e animal</div>
                                        </div>
                                        <div className="px-3 py-2 rounded-2xl bg-white/15 text-white text-xs font-bold backdrop-blur">
                                            Entrar
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="p-4">
                                <div className="text-sm text-secondary">
                                    Escolha o valor, selecione o sorteio e depois o animal.
                                </div>
                            </div>
                        </button>

                        <button
                            type="button"
                            onClick={() => router.push('/app/loteria')}
                            className="group text-left bg-white border-2 border-gray-200 rounded-3xl overflow-hidden shadow-lg hover:border-primary/50 hover:shadow-xl transition-all active:scale-[0.99]"
                        >
                            <div className="relative">
                                <img className="w-full h-44 object-cover" src="/images/loteria.png" />
                                <div className="absolute inset-0 bg-gradient-to-t from-black/55 via-black/10 to-transparent"></div>
                                <div className="absolute bottom-3 left-3 right-3">
                                    <div className="flex items-center justify-between gap-3">
                                        <div>
                                            <div className="text-white font-bold text-lg">Loterias</div>
                                            <div className="text-white/90 text-xs">Modalidade e palpites</div>
                                        </div>
                                        <div className="px-3 py-2 rounded-2xl bg-white/15 text-white text-xs font-bold backdrop-blur">
                                            Entrar
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="p-4">
                                <div className="text-sm text-secondary">
                                    Selecione a modalidade, preencha seus palpites e finalize.
                                </div>
                            </div>
                        </button>
                    </div>
                </div>

                <div className="mt-4 mb-28">
                    <button
                        type="button"
                        onClick={() => router.push('/app/financeiro')}
                        className="bg-degrade-success text-white p-4 flex items-center justify-between rounded-3xl drop-shadow-lg relative w-full hover:opacity-95 transition-opacity"
                    >
                        <div className="w-20 absolute -left-4">
                            <img src="/images/coinTwo.png" className="w-full" />
                        </div>
                        <div className="ml-14 whitespace-nowrap mr-2">
                            <div className="font-bold text-xl">Recarga PIX</div>
                            <div>
                                <small>Recarga Imediata</small>
                            </div>
                        </div>
                        <div>
                            <img src="/images/pix.png" />
                        </div>
                    </button>
                </div>

                {/*<div className="mt-4">*/}
                {/*    <div className="grid grid-cols-4 gap-4">*/}
                {/*        <button className="aspect-square flex justify-center items-center border-primary border-2 p-3 rounded-xl">*/}
                {/*            <img src="/images/pepicons-pop_dollar.svg"/>*/}
                {/*        </button>*/}
                {/*        <button className="aspect-square flex justify-center items-center border-primary border-2 p-3 rounded-xl">*/}
                {/*            <img src="/images/pepicons-pop_dollar.svg"/>*/}
                {/*        </button>*/}
                {/*        <button className="aspect-square flex justify-center items-center border-primary border-2 p-3 rounded-xl">*/}
                {/*            <img src="/images/carbon_result.svg"/>*/}
                {/*        </button>*/}
                {/*        <button className="aspect-square flex justify-center items-center border-primary border-2 p-3 rounded-xl">*/}
                {/*            <img src="/images/mingcute_whatsapp-line.svg"/>*/}
                {/*        </button>*/}
                {/*    </div>*/}
                {/*</div>*/}

            </div>
        </div>
    )
}

export default Home;