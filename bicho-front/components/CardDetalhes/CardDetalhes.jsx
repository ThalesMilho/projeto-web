const CardDetalhes = function( { children, disabled, border }) {
    return (
        <div className={`radioButton font-bold flex justify-center items-center transition-all w-full text-gray-500 ${border ? border : 'border-2'} box-shadow-forte-y border-primary p-2 rounded-md ${disabled ? 'opacity-70':''}`}>
            { children }
        </div>
    );
}

export default CardDetalhes;