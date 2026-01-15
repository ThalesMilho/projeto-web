import CardDetalhes from "@/components/CardDetalhes/CardDetalhes";

const RadioButton = function({ value, name, label, onChange, disabled }) {
    return (
        <label className="cursor-pointer hover:scale-105 transition-all">
            <input disabled={disabled} value={value} onChange={onChange} type="radio" className="hidden" name={name}/>
            <CardDetalhes disabled={disabled}>{label}</CardDetalhes>
        </label>
    );
}

export default RadioButton;