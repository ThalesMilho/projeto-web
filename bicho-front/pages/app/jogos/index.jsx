import UltimoGanhador from "@/components/UltimoGanhador/UltimoGanhador";
import { DollarSign } from 'lucide-react';
import UltimoGanhador2 from "@/components/UltimoGanhador/UltimoGanhador2";

const Home = function() {
    return (
        <div>

            <div className="flex gap-4 overflow-x-auto hide-scrollbar p-4">
                <UltimoGanhador2 />
                <UltimoGanhador2 />
                <UltimoGanhador2 />
                <UltimoGanhador2 />
            </div>

            <div className="p-4">
                <div>
                    <h3 className="font-bold text-xl">Selecione um jogo</h3>
                    <div className="grid grid-cols-2 gap-4 mt-2">
                        <div>
                            <img className="rounded-2xl drop-shadow-lg" src="/images/bicho.png" />
                            <div className="mt-3 font-semibold text-center">Jogo do bicho</div>
                        </div>
                        <div>
                            <img className="rounded-2xl drop-shadow-lg" src="/images/loteria.png" />
                            <div className="mt-3 font-semibold text-center">Loterias</div>
                        </div>
                    </div>
                </div>

                <div className="mt-4">
                    <button className="bg-degrade-success text-white p-4 flex items-center justify-between rounded-3xl drop-shadow-lg relative w-full">
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