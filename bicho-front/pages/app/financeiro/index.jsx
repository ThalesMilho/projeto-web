import {useState} from "react";
import RecargaPage from "@/pages/app/financeiro/Recarga";
import SaquePage from "@/pages/app/financeiro/Saque";
import Head from "next/head";

const Financeiro = function() {

    const [activeTab, setActiveTab] = useState("tab1");

    return (
        <div className="container mx-auto p-4">
            <Head>
                <title>Financeiro</title>
            </Head>
            <div className="w-full">
                <div className="flex space-x-4 border-b-2 border-primary">
                    {/* Tab Buttons */}
                    <button
                        className={`py-2 px-4 ${
                            activeTab === "tab1"
                                ? "border-b-4 border-primary text-primary font-bold"
                                : "font-semibold"
                        }`}
                        onClick={() => setActiveTab("tab1")}
                    >
                        Realizar recarga
                    </button>
                    <button
                        className={`py-2 px-4 ${
                            activeTab === "tab2"
                                ? "border-b-4 border-primary text-primary font-bold"
                                : " font-semibold"
                        }`}
                        onClick={() => setActiveTab("tab2")}
                    >
                        Solicitar saque
                    </button>
                </div>

                {/* Tab Content */}
                <div className="mt-4">
                    {activeTab === "tab1" && (
                        <div className="fade-in">
                            <RecargaPage />
                        </div>
                    )}
                    {activeTab === "tab2" && (
                        <div className="fade-in">
                            <SaquePage />
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
        ;
}

export default Financeiro;