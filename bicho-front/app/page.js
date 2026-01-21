"use client";

import {useEffect} from "react";

export default function Home() {

    useEffect(() => {
        window.location.href = "/app/jogos";
    }, []);

    return (
        <div className="bg-gradient-to-b bg-tertiary min-h-screen text-white flex flex-col items-center justify-center">

        </div>
    );
}
