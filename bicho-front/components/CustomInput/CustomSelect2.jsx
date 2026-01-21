const CustomSelect2 = function({ label, data=[], ...rest }) {
    return (
        <div>
            {label && (
                <Capsula label={label} />
            )}
            <div className="rounded-md bg-tertiary h-10 text-white border-2 border-tertiary">
                <select {...rest} className="cursor-pointer w-full h-full bg-transparent outline-0 px-4">
                    {
                        data.map((item, index) => <option className="text-secondary" key={index} value={item.value}>{item.label}</option>)
                    }
                </select>
            </div>
        </div>
    );
}

const Capsula = function ({label, children}) {
    if (label) {
        return (<label>
            <div className="text-white mb-1 text-sm opacity-50">{label}</div>
            {children}
        </label>)
    } else {
        return children;
    }
}
export default CustomSelect2;