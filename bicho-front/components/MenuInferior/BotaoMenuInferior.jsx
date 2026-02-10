const BotaoMenuInferior = function({active, Icon, setActive, index}) {

    const changeTo = function(indexAtivado) {
        setActive(indexAtivado);
    }

    return (
        <button className="w-full h-full py-2" onClick={() => changeTo(index)}>
            <div className="w-full h-full flex flex-col items-center justify-center gap-1">
                <div
                    className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all ${
                        active
                            ? 'bg-primary/10 shadow-sm'
                            : 'bg-transparent'
                    }`}
                >
                    <Icon color={active ? "#3C7FFF" : "#6B7280"} size={26}/>
                </div>
                <div className={`h-1 w-8 rounded-full transition-all ${active ? 'bg-primary' : 'bg-transparent'}`}></div>
            </div>
        </button>
    );
}

export default BotaoMenuInferior;