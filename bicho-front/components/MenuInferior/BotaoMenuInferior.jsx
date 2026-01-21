const BotaoMenuInferior = function({active, Icon, setActive, index}) {

    const changeTo = function(indexAtivado) {
        setActive(indexAtivado);
    }

    return (
        <button className="pt-1" onClick={() => changeTo(index)}>
            <div
                className={`w-full flex justify-center items-center -translate-y-1 rounded-2xl ${active ? "bg-white -translate-y-8" : "bg-transparent"} aspect-square!`}  style={ active ? {boxShadow: "0 0 10px 0px #3C7FFF",width: 80, height: 80} : {}}>
                <div className={`transition-all text-white ${active ? "scale-150" : ""}`}>
                    <Icon color={active ? "#3C7FFF" : "#fff"} size={30}/>
                </div>
            </div>
        </button>
    );
}

export default BotaoMenuInferior;