import {useState} from "react";

const Tabs = function({ tabs=[] }) {

    const [activeTab, setActiveTab] = useState(0);

    return (
        <div className="border-border border rounded-2xl">
            <div className="flex justify-between">
                {tabs.map((tab,index) => (
                    <button key={index} onClick={() => setActiveTab(index)} className={`first:rounded-tl-2xl last:rounded-tr-2xl ${index == activeTab ? 'bg-success-linear' : 'bg-foreground'} w-full h-12 text-center`}>{tab?.titulo}</button>
                ))}
            </div>
            <div className="relative overflow-hidden bg-quadrado">
                {/* <img src="/images/quadradoBackground.png" className="absolute right-0 top-0" style={{ height: 100, maxHeight: 200, zIndex: 0 }}/> */}
                <div>
                    {tabs[activeTab]?.render}
                </div>
            </div>
        </div>
    );
}

export default Tabs;