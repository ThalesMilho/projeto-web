import Image from "next/image";
import Link from "next/link";
import { useContext, useEffect, useState, useRef } from "react";
import { ContextoUsuario } from "@/pages/_app";
import { toMoney } from "@/helpers/functions";
import { FaBars, FaTimes, FaGamepad, FaMoneyBillWave, FaWallet, FaHistory, FaUser, FaSignOutAlt, FaBell, FaTrophy, FaCheckCircle, FaInfoCircle, FaGift } from "react-icons/fa";
import { useRouter } from 'next/router';
import logo from "@/public/images/logo.png";

const Header = function () {

    const logo = require("./../../public/images/logo.png");
    const [dadosUsuarioLogado, setDadosUsuarioLogado] = useContext(ContextoUsuario);
    const [saldo, setSaldo] = useState(0);
    const userBalance = typeof saldo === 'number' ? toMoney(saldo) : 'R$ 0,00';
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isNotificationOpen, setIsNotificationOpen] = useState(false);
    const notificationRef = useRef(null);
    const router = useRouter();

    // Mock notifications data - replace with real data
    const [notifications, setNotifications] = useState([
        { id: 1, title: "Novo prêmio disponível!", message: "Você ganhou R$ 150,00 no jogo do bicho", time: "5 min atrás", read: false, type: "prize" },
        { id: 2, title: "Recarga confirmada", message: "Sua recarga de R$ 50,00 foi processada", time: "1 hora atrás", read: false, type: "payment" },
        { id: 3, title: "Resultado do sorteio", message: "Confira os resultados do último sorteio", time: "2 horas atrás", read: true, type: "info" },
        // { id: 4, title: "Bônus especial!", message: "Você recebeu um bônus de R$ 25,00", time: "3 horas atrás", read: true, type: "bonus" },
    ]);

    // Get icon and color based on notification type
    const getNotificationIcon = (type) => {
        switch(type) {
            case 'prize':
                return { icon: <FaTrophy size={20} />, color: 'text-yellow-500', bg: 'bg-yellow-50' };
            case 'payment':
                return { icon: <FaCheckCircle size={20} />, color: 'text-green-500', bg: 'bg-green-50' };
            case 'bonus':
                return { icon: <FaGift size={20} />, color: 'text-purple-500', bg: 'bg-purple-50' };
            case 'info':
            default:
                return { icon: <FaInfoCircle size={20} />, color: 'text-blue-500', bg: 'bg-blue-50' };
        }
    };

    const unreadCount = notifications.filter(n => !n.read).length;

    const menuItems = [
        { name: 'Jogos', path: '/app/jogos', icon: <FaGamepad size={20} /> },
        { name: 'Depositar', path: '/app/financeiro', icon: <FaMoneyBillWave size={20} /> },
        // { name: 'Saldo', path: '/saldo', icon: <FaWallet size={20} /> },
        { name: 'Histórico', path: '/app/historico', icon: <FaHistory size={20} /> },
        { name: 'Perfil', path: '/app/perfil', icon: <FaUser size={20} /> },
        { name: 'Sair', path: '/sair', icon: <FaSignOutAlt size={20} /> },
    ];

    const toggleMenu = () => {
        setIsMenuOpen(!isMenuOpen);
    };

    const toggleNotifications = () => {
        setIsNotificationOpen(!isNotificationOpen);
    };

    const markAsRead = (id) => {
        setNotifications(notifications.map(n => 
            n.id === id ? { ...n, read: true } : n
        ));
    };

    const handleNavigation = (path) => {
        router.push(path);
        toggleMenu();
    };

    // Close notification popup when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (notificationRef.current && !notificationRef.current.contains(event.target)) {
                setIsNotificationOpen(false);
            }
        };

        if (isNotificationOpen) {
            document.addEventListener('mousedown', handleClickOutside);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [isNotificationOpen]);

    useEffect(() => {
        if(dadosUsuarioLogado?.id) {
            window.Echo.private(`saldo.${dadosUsuarioLogado?.id}`).listen(".saldo_atualizado", function(data) {
                setDadosUsuarioLogado({
                    ...dadosUsuarioLogado,
                    saldo: data.saldo
                });
            });
        }

        if(dadosUsuarioLogado?.saldo) {
            setSaldo(parseFloat(dadosUsuarioLogado?.saldo));
        } else {
            setSaldo(0);
        }

    }, [dadosUsuarioLogado]);

    return (
        <header className="text-white relative">
            <div className="bg-degrade rounded-br-3xl rounded-bl-3xl p-4 py-6 shadow-lg">
                <div className="flex justify-between items-center text-white">
                    <div className="flex items-center">
                        <button 
                            onClick={toggleMenu}
                            className="mr-4 focus:outline-none md:hidden p-2 rounded-xl hover:bg-white/10 transition-colors"
                            aria-label="Menu"
                        >
                            {isMenuOpen ? <FaTimes size={24} /> : <FaBars size={24} />}
                        </button>
                        <div className="flex items-center">
                            <span className="font-bold">Maior Bicho</span>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        {/* Notification Bell */}
                        <div className="relative" ref={notificationRef}>
                            <button
                                onClick={toggleNotifications}
                                className="relative focus:outline-none p-2 rounded-xl hover:bg-white/10 transition-colors"
                                aria-label="Notificações"
                            >
                                <FaBell size={24} />
                                {unreadCount > 0 && (
                                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                                        {unreadCount}
                                    </span>
                                )}
                            </button>

                            {/* Notification Popup */}
                            {isNotificationOpen && (
                                <>
                                    {/* Mobile backdrop */}
                                    <div className="fixed inset-0 bg-black bg-opacity-80 z-40 md:hidden" onClick={toggleNotifications}></div>
                                    
                                    {/* Popup */}
                                    <div className="fixed md:absolute left-0 right-0 md:left-auto md:right-0 top-0 md:top-auto md:mt-2 w-full md:w-96 bg-white md:rounded-lg shadow-xl z-50 overflow-hidden max-h-[80vh] md:max-h-[500px] flex flex-col">
                                        <div className="bg-degrade p-4 text-white font-bold flex justify-between items-center">
                                            <span>Notificações</span>
                                            <button 
                                                onClick={toggleNotifications}
                                                className="md:hidden text-white hover:opacity-80"
                                            >
                                                <FaTimes size={20} />
                                            </button>
                                        </div>
                                        <div className="flex-1 overflow-y-auto">
                                            {notifications.length === 0 ? (
                                                <div className="p-4 text-center text-gray-500">
                                                    Nenhuma notificação
                                                </div>
                                            ) : (
                                                notifications.map((notification) => (
                                                    <div
                                                    key={notification.id}
                                                    onClick={() => markAsRead(notification.id)}
                                                    className={`p-4 border-b border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors ${
                                                        !notification.read ? 'bg-blue-50' : ''
                                                    }`}
                                                >
                                                    <div className="flex items-start gap-3">
                                                        {/* Icon */}
                                                        <div className={`flex-shrink-0 w-10 h-10 rounded-full ${getNotificationIcon(notification.type).bg} flex items-center justify-center ${getNotificationIcon(notification.type).color}`}>
                                                            {getNotificationIcon(notification.type).icon}
                                                        </div>
                                                        
                                                        {/* Content */}
                                                        <div className="flex-1 min-w-0">
                                                            <div className="font-semibold text-gray-800 flex items-center">
                                                                {notification.title}
                                                                {!notification.read && (
                                                                    <span className="ml-2 w-2 h-2 bg-blue-500 rounded-full flex-shrink-0"></span>
                                                                )}
                                                            </div>
                                                            <div className="text-sm text-gray-600 mt-1">
                                                                {notification.message}
                                                            </div>
                                                            <div className="text-xs text-gray-400 mt-1">
                                                                {notification.time}
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                                ))
                                            )}
                                        </div>
                                        <div className="p-3 bg-gray-50 text-center border-t border-gray-200">
                                            <button className="text-sm text-primary font-semibold hover:underline">
                                                Ver todas as notificações
                                            </button>
                                        </div>
                                    </div>
                                </>
                            )}
                        </div>

                        {/* Balance */}
                        <button
                            type="button"
                            onClick={() => router.push('/app/financeiro')}
                            className="px-3 py-2 rounded-2xl border border-white/25 bg-white/10 backdrop-blur shadow-sm hover:bg-white/15 transition-colors"
                            aria-label="Ver saldo"
                        >
                            <span className="text-xs font-semibold text-white/90">Saldo</span>
                            <div className="text-sm font-bold leading-tight">{userBalance}</div>
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Menu */}
            <div 
                className={`fixed inset-0 z-50 ${isMenuOpen ? 'block' : 'pointer-events-none'} md:hidden`}
            >
                {/* Background with fade animation */}
                <div 
                    className={`fixed inset-0 bg-black transition-opacity duration-300 ${
                        isMenuOpen ? 'opacity-75' : 'opacity-0'
                    }`} 
                    onClick={toggleMenu}
                ></div>
                
                {/* Menu with slide animation */}
                <div 
                    className={`fixed inset-y-0 left-0 w-4/5 bg-degrade p-6 transform transition-transform duration-300 ease-in-out ${
                        isMenuOpen ? 'translate-x-0' : '-translate-x-full'
                    }`}
                >
                    <div className="flex justify-between items-center mb-8">
                        <div className="flex items-center">
                            <Image 
                                src={logo} 
                                alt="Maior Bicho Logo" 
                                width={32} 
                                height={32} 
                                className="mr-2"
                                priority
                            />
                            <h2 className="text-xl font-bold">Menu</h2>
                        </div>
                        <button onClick={toggleMenu} className="text-white focus:outline-none">
                            <FaTimes size={24} />
                        </button>
                    </div>
                    <nav className="space-y-4">
                        {menuItems.map((item, index) => (
                            <button
                                key={index}
                                onClick={() => handleNavigation(item.path)}
                                className="w-full flex items-center p-3 rounded-lg hover:bg-white hover:bg-opacity-20 transition-colors duration-200 text-left"
                            >
                                <div className="mr-3">{item.icon}</div>
                                {item.name}
                            </button>
                        ))}
                    </nav>
                </div>
            </div>

        </header>
    );
}

export default Header;