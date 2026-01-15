import {MoveLeft} from "lucide-react";

const ButtonVoltar = function() {
    return (
        <button type="button"
                className="text-primary flex justify-center p-2 bg-white bg-opacity-10 w-fit items-center rounded-md mt-4">
            <MoveLeft className="text-primary"/>
            <div className="ml-2">Voltar</div>
        </button>
    );
}

export default ButtonVoltar;