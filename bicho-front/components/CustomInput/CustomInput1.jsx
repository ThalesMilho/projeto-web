
import { InputMask } from '@react-input/mask';
import {InputNumberFormat} from "@react-input/number-format";

const CustomInput1 = function ({ textarea=false, light, currency=false, label, name, placeholder, required, type="text", customValidation, ...rest }) {

    return (
        <div>
            <Capsula label={label} light={light}>
                {
                    rest.mask &&
                        (<InputMask
                            required={required}
                            type={type}
                            name={name}
                            placeholder={placeholder}
                            {...rest}
                            className={"w-full h-14 rounded-2xl px-4 outline-0 bg-foreground text-white disabled:opacity-70 "+(rest?.className ?? "")}
                        />)
                }
                {
                    currency &&
                        (<InputNumberFormat
                            locales="pt-BR"
                            decimals={2}
                            maximumFractionDigits={2}
                            required={required}
                            type={type}
                            name={name}
                            placeholder={placeholder}
                            {...rest}
                            className={"w-full h-14 rounded-2xl px-4 outline-0 bg-foreground text-white disabled:opacity-70 "+(rest?.className ?? "")}
                        />)
                }
                {
                    (!rest.mask && !currency) &&
                        (
                            textarea ?
                                <textarea
                                    required={required}
                                    name={name}
                                    placeholder={placeholder}
                                    {...rest}
                                    className={"w-full h-24 rounded-2xl px-4 pt-2 outline-0 bg-foreground text-white disabled:opacity-70 resize-none "+(rest?.className ?? "")}
                                ></textarea>
                                :
                                <input
                                    required={required}
                                    type={type}
                                    name={name}
                                    placeholder={placeholder}
                                    {...rest}
                                    className={"w-full h-14 rounded-2xl px-4 outline-0 bg-foreground text-white disabled:opacity-70 "+(rest?.className ?? "")}
                                />
                        )
                }
            </Capsula>
        </div>
    );
}

const Capsula = function({ label, children, light }) {
    if(label) {
        return (<label>
            <div className={"mb-1 " + (light ? "text-white" : "")}>{label}</div>
            {children}
        </label>)
    } else {
        return children;
    }
}
//
// const CustomInput2 = function(props) {
//     return CustomInput1({...props, className: "w-full h-14 rounded-2xl px-4 outline-0 bg-foreground text-white disabled:opacity-70"});
// }

export default CustomInput1;
