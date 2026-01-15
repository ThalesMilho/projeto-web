const CustomSelect1 = function({ data=[] }) {
    return (
        <div className="h-8 rounded-full bg-transparent px-4 text-secondary border-2 border-tertiary">
            <select className="cursor-pointer w-full h-full bg-transparent outline-0">
                {
                    data.map((item, index) => <option key={index} value={item.value}>{item.label}</option>)
                }
            </select>
        </div>
    );
}

export default CustomSelect1;