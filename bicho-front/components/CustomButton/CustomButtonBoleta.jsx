import CircularLoadCustom from "@/components/icons/CircularLoadCustom";

const CustomButtonBoleta = function ({ multiplicador=null, bgColor="bg-tertiary", active=false, disabled, loading=false, label, transparent=false, type="submit", className, onClick, ...rest }) {

    return (
        <button
            type={type}
            onClick={onClick}
            className={`min-w-16 ${className ? className : ''} flex flex-col transition-all justify-center items-center w-full h-14 px-4 text-secondary outline-0 ${transparent ? 'bg-transparent' : bgColor+" shadow-lg"} ${active ? '!bg-primary': ''} ${active ? '!text-white': ''} disabled:opacity-70`}
            disabled={disabled || loading}
            {...rest}
        >
            {
                loading && (
                    <div className="mr-2">
                        <CircularLoadCustom color="#fff" />
                    </div>
                )
            }
            {label}
            {
                multiplicador && (
                    <div className={`font-light ${active ? 'text-white' : 'text-yellow-400'}`}>
                        {multiplicador}{multiplicador && "x"}
                    </div>
                )
            }
        </button>
    );
}

export default CustomButtonBoleta;