const MensagemComponent = function({nome, data, mensagem, me}) {

    return (
        <li className={`w-full ${me ? 'flex flex-col items-end' : ''}`}>
            <small>{nome}</small>
            <div className={`${me ? "bg-primary" : "bg-background-secondary"} rounded p-2 w-fit max-w-[90%] mb-2`}>
                <p>{mensagem}</p>
                <small className="whitespace-nowrap">{data}</small>
            </div>
        </li>
    );
}

export default MensagemComponent;