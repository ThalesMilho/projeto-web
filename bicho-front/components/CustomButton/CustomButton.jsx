import CircularLoadCustom from "@/components/icons/CircularLoadCustom";
import {useEffect, useState} from "react";

const CustomButton = function ({ bgColor="bg-primary", disabled, loading=false, label, transparent=false, type="submit", className, onClick, ...rest }) {

    return (
        <button
            type={type}
            onClick={onClick}
            className={`rounded-full ${className ? className : ''} flex justify-center items-center w-full h-10 px-4 text-white outline-0 ${transparent ? 'bg-transparent' : bgColor+" shadow-lg"} disabled:opacity-70`}
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
        </button>
    );
}

export default CustomButton;