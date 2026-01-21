import {useState} from "react";
import RecargaPage from "@/pages/app/financeiro/Recarga";
import SaquePage from "@/pages/app/financeiro/Saque";
import SolicitacoesSaquePage from "@/pages/app/saques/SolicitacoesSaques";
import RecargasUsuarios from "@/pages/app/saques/RecargasUsuarios";
import Head from "next/head";

const SaquesPage = function() {

    const [activeTab, setActiveTab] = useState("tab1");

    return (
        <div className="container mx-auto p-4">
            <Head>
                <title>Saques de usuários</title>
            </Head>
            <div className="w-full">
                <div className="flex space-x-4 border-b-2 border-primary">
                    {/* Tab Buttons */}
                    <button
                        className={`py-2 px-4 ${
                            activeTab === "tab1"
                                ? "border-b-4 border-primary text-primary font-bold"
                                : "text-secondary font-semibold"
                        }`}
                        onClick={() => setActiveTab("tab1")}
                    >
                        Solicitações de saque
                    </button>
                    <button
                        className={`py-2 px-4 ${
                            activeTab === "tab2"
                                ? "border-b-4 border-primary text-primary font-bold"
                                : "text-secondary font-semibold"
                        }`}
                        onClick={() => setActiveTab("tab2")}
                    >
                        Recargas de usuários
                    </button>
                </div>

                {/* Tab Content */}
                <div className="mt-4">
                    {activeTab === "tab1" && (
                        <div className="fade-in">
                            <SolicitacoesSaquePage />
                        </div>
                    )}
                    {activeTab === "tab2" && (
                        <div className="fade-in">
                            <RecargasUsuarios />
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
        ;
}

export default SaquesPage;