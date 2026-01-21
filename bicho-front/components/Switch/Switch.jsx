import ReactSwitch from "react-switch";

const Switch = function({checked, onChange, label, disabled}) {
    return (
        <div className="">
            <label>
                <div className="flex items-center">
                    <div className="scale-75">
                        <ReactSwitch
                            checked={checked}
                            onChange={onChange}
                            disabled={disabled}
                            onColor="#2D9383"
                            onHandleColor="#fff"
                            handleDiameter={30}
                            uncheckedIcon={false}
                            checkedIcon={false}
                            boxShadow="0px 1px 5px rgba(0, 0, 0, 0.6)"
                            activeBoxShadow="0px 0px 1px 10px rgba(0, 0, 0, 0.2)"
                            height={20}
                            width={48}
                            className="react-switch"
                        />
                    </div>
                    {
                        label && (<Capsula label={label}/>)
                    }
                </div>
            </label>
        </div>
    );
}

const Capsula = function ({label, children}) {
    if (label) {
        return (<div className="cursor-pointer">
            <div className="text-white mb-1 text-sm opacity-50">{label}</div>
            {children}
        </div>)
    } else {
        return children;
    }
}

export default Switch;