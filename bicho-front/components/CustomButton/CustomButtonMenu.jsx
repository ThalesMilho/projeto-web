const CustomButtonMenu = function ({ bgColor="bg-tertiary", active=false, disabled, label, transparent=false, type="button", className, onClick, Icon, ...rest }) {

    return (
        <button
            type={type}
            onClick={onClick}
            className={`${className ? className : ''} flex transition-all items-center w-full h-10 px-4 text-secondary outline-0 ${transparent ? 'bg-transparent' : bgColor+" shadow-lg"} ${active ? '!bg-primary': ''} ${active ? '!text-white': ''} disabled:opacity-70`}
            disabled={disabled}
            {...rest}
        >
            {
                Icon && (
                    <div className="mr-2">
                        <Icon size={16}  />
                    </div>
                )
            }
            {label}
        </button>
    );
}

export default CustomButtonMenu;