import { useEffect, useMemo, useState } from 'react';
import { ChevronDown, ChevronLeft, Search } from 'lucide-react';
import ClockCustom from '@/components/icons/ClockCustom';
import { theme } from '@/tailwind.config';
import LoadCenter from '@/components/icons/LoadCenter';
import moment from 'moment/moment';
import { toMoney } from '@/helpers/functions';
import { useRouter } from 'next/router';
import Head from 'next/head';

const Historico = function() {
    const router = useRouter();

    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const [searchTerm, setSearchTerm] = useState('');
    const [expandedIds, setExpandedIds] = useState({});

    const apostasMock = useMemo(
        () => [
            {
                id: 12091,
                jogo: 'Loterias',
                loteriaNome: 'LOTERIA',
                modalidadeNome: 'CENTENA',
                posicaoNome: '1º Prêmio',
                created_at: '2026-02-03T16:05:12.000Z',
                sorteio: {
                    data: '2026-02-03T20:45:00.000Z',
                    nome: 'Sorteio de Hoje'
                },
                valorAposta: 10,
                palpites: [{ display: '123' }, { display: '045' }],
                status: 'pending',
                resultado: null
            },
            {
                id: 12044,
                jogo: 'Loterias',
                loteriaNome: 'SENINHA',
                modalidadeNome: 'SENINHA 10D',
                created_at: '2026-02-02T14:22:41.000Z',
                sorteio: {
                    data: '2026-02-02T20:45:00.000Z',
                    nome: 'Sorteio - Domingo'
                },
                valorAposta: 5,
                palpites: [
                    { numbers: [1, 4, 9, 13, 22, 31, 44, 55, 70, 80] },
                    { numbers: [2, 5, 11, 14, 23, 33, 46, 57, 71, 79] }
                ],
                status: 'won',
                resultado: {
                    premio: 125,
                    created_at: '2026-02-02T21:03:10.000Z',
                    resumo: 'Parabéns! Você acertou 10 dezenas.'
                }
            },
            {
                id: 12012,
                jogo: 'Loterias',
                loteriaNome: 'QUININHA',
                modalidadeNome: 'QUININHA 13D',
                created_at: '2026-02-01T10:11:08.000Z',
                sorteio: {
                    data: '2026-02-01T20:45:00.000Z',
                    nome: 'Sorteio - Sábado'
                },
                valorAposta: 7.5,
                palpites: [{ numbers: [3, 7, 8, 14, 21, 30, 35, 41, 52, 60, 68, 72, 77] }],
                status: 'lost',
                resultado: {
                    premio: 0,
                    created_at: '2026-02-01T21:02:43.000Z',
                    resumo: 'Não foi dessa vez. Boa sorte na próxima!'
                }
            }
        ],
        []
    );

    useEffect(() => {
        const t = setTimeout(() => setLoading(false), 250);
        return () => clearTimeout(t);
    }, []); // eslint-disable-line react-hooks/exhaustive-deps

    const statusMeta = (status) => {
        if (status === 'won') {
            return {
                label: 'Ganhou',
                badge: 'bg-green-100 text-green-700 border-green-200',
                amountClass: 'text-success-dark'
            };
        }
        if (status === 'lost') {
            return {
                label: 'Perdeu',
                badge: 'bg-red-100 text-red-700 border-red-200',
                amountClass: 'text-red-500'
            };
        }
        return {
            label: 'Aguardando',
            badge: 'bg-yellow-100 text-yellow-700 border-yellow-200',
            amountClass: 'text-yellow-600'
        };
    };

    const toggleExpanded = (id) => {
        setExpandedIds((prev) => ({
            ...prev,
            [id]: !prev[id]
        }));
    };

    const filteredApostas = useMemo(() => {
        const s = (searchTerm || '').trim().toLowerCase();

        return apostasMock.filter((aposta) => {
            const matchesFilter =
                filter === 'all' ? true : (aposta.status || 'pending') === filter;

            if (!matchesFilter) return false;
            if (!s) return true;

            const haystack = [
                aposta.loteriaNome,
                aposta.modalidadeNome,
                aposta.posicaoNome,
                String(aposta.id)
            ]
                .filter(Boolean)
                .join(' ')
                .toLowerCase();

            return haystack.includes(s);
        });
    }, [apostasMock, filter, searchTerm]);

    const summary = useMemo(() => {
        const totalApostado = apostasMock.reduce((acc, a) => acc + (Number(a.valorAposta) || 0), 0);
        const totalRetorno = apostasMock.reduce(
            (acc, a) => acc + (a.status === 'won' ? (Number(a?.resultado?.premio) || 0) : 0),
            0
        );
        const totalLiquidado = totalRetorno - apostasMock.reduce(
            (acc, a) => acc + ((a.status === 'pending' ? 0 : (Number(a.valorAposta) || 0))),
            0
        );

        const wins = apostasMock.filter((a) => a.status === 'won').length;
        const losses = apostasMock.filter((a) => a.status === 'lost').length;
        const pending = apostasMock.filter((a) => a.status === 'pending').length;

        return {
            totalApostado,
            totalRetorno,
            totalLiquidado,
            wins,
            losses,
            pending
        };
    }, [apostasMock]);

    return (
        <div className="min-h-screen bg-background mb-10">
            <Head>
                <title>Histórico de partidas</title>
            </Head>

            <div className="p-4 pb-24 md:pl-64 lg:pl-72">
                {loading ? (
                    <LoadCenter />
                ) : (
                    <>
                        <div className="mb-4">
                            <h2 className="font-bold text-xl">Suas apostas</h2>
                            <p className="text-sm text-secondary mt-1">
                                Acompanhe resultados, valores e detalhes das suas apostas
                            </p>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
                            <div className="bg-white rounded-2xl border-2 border-gray-200 p-4 shadow-lg">
                                <div className="text-xs font-semibold text-secondary">TOTAL APOSTADO</div>
                                <div className="text-lg font-bold text-gray-800 mt-1">{toMoney(summary.totalApostado)}</div>
                                <div className="text-xs text-secondary mt-2">
                                    {summary.wins} ganha(s), {summary.losses} perdida(s), {summary.pending} pendente(s)
                                </div>
                            </div>
                            <div className="bg-white rounded-2xl border-2 border-gray-200 p-4 shadow-lg">
                                <div className="text-xs font-semibold text-secondary">TOTAL RETORNO</div>
                                <div className="text-lg font-bold text-success-dark mt-1">{toMoney(summary.totalRetorno)}</div>
                                <div className="text-xs text-secondary mt-2">Somente apostas ganhas</div>
                            </div>
                            <div className="bg-white rounded-2xl border-2 border-gray-200 p-4 shadow-lg">
                                <div className="text-xs font-semibold text-secondary">SALDO (LIQUIDADO)</div>
                                <div
                                    className={`text-lg font-bold mt-1 ${
                                        summary.totalLiquidado >= 0 ? 'text-success-dark' : 'text-red-500'
                                    }`}
                                >
                                    {summary.totalLiquidado >= 0 ? '+' : ''}{toMoney(summary.totalLiquidado)}
                                </div>
                                <div className="text-xs text-secondary mt-2">Não inclui apostas pendentes</div>
                            </div>
                        </div>

                        <div className="bg-white rounded-2xl border-2 border-gray-200 p-4 shadow-lg mb-4">
                            <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                                <div className="relative flex-1">
                                    <Search
                                        className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary"
                                        size={18}
                                    />
                                    <input
                                        type="text"
                                        value={searchTerm}
                                        onChange={(e) => setSearchTerm(e.target.value)}
                                        placeholder="Buscar por ID, modalidade ou posição..."
                                        className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-primary transition-colors"
                                    />
                                </div>
                                <div className="flex items-center gap-2 overflow-x-auto hide-scrollbar">
                                    <button
                                        onClick={() => setFilter('all')}
                                        className={`px-4 py-2 rounded-xl border-2 text-sm font-bold transition-all whitespace-nowrap ${
                                            filter === 'all'
                                                ? 'bg-primary text-white border-primary'
                                                : 'bg-white text-gray-700 border-gray-200 hover:border-primary/50'
                                        }`}
                                    >
                                        Todas
                                    </button>
                                    <button
                                        onClick={() => setFilter('pending')}
                                        className={`px-4 py-2 rounded-xl border-2 text-sm font-bold transition-all whitespace-nowrap ${
                                            filter === 'pending'
                                                ? 'bg-primary text-white border-primary'
                                                : 'bg-white text-gray-700 border-gray-200 hover:border-primary/50'
                                        }`}
                                    >
                                        Aguardando
                                    </button>
                                    <button
                                        onClick={() => setFilter('won')}
                                        className={`px-4 py-2 rounded-xl border-2 text-sm font-bold transition-all whitespace-nowrap ${
                                            filter === 'won'
                                                ? 'bg-primary text-white border-primary'
                                                : 'bg-white text-gray-700 border-gray-200 hover:border-primary/50'
                                        }`}
                                    >
                                        Ganhas
                                    </button>
                                    <button
                                        onClick={() => setFilter('lost')}
                                        className={`px-4 py-2 rounded-xl border-2 text-sm font-bold transition-all whitespace-nowrap ${
                                            filter === 'lost'
                                                ? 'bg-primary text-white border-primary'
                                                : 'bg-white text-gray-700 border-gray-200 hover:border-primary/50'
                                        }`}
                                    >
                                        Perdidas
                                    </button>
                                </div>
                            </div>
                        </div>

                        {filteredApostas.length === 0 ? (
                            <div className="flex items-center flex-col mt-10">
                                <p className="text-secondary mb-3">Nenhuma aposta encontrada</p>
                                <ClockCustom color={theme.extend.colors.secondary} size={75} />
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {filteredApostas.map((aposta) => {
                                    const meta = statusMeta(aposta.status);
                                    const expanded = !!expandedIds[aposta.id];

                                    return (
                                        <div
                                            key={aposta.id}
                                            className="bg-white border-2 border-gray-200 rounded-2xl p-4 shadow-lg"
                                        >
                                            <div className="flex items-start justify-between gap-3">
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-2 flex-wrap">
                                                        <div className="font-bold text-base text-gray-900">#{aposta.id}</div>
                                                        <span
                                                            className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold border ${meta.badge}`}
                                                        >
                                                            {meta.label}
                                                        </span>
                                                    </div>

                                                    <div className="mt-2">
                                                        <div className="font-bold text-primary">
                                                            {(aposta.loteriaNome || aposta.jogo || 'APOSTA').toString()}
                                                        </div>
                                                        <div className="text-sm text-secondary mt-0.5">
                                                            {aposta.modalidadeNome}
                                                            {aposta.posicaoNome ? ` • ${aposta.posicaoNome}` : ''}
                                                        </div>
                                                    </div>
                                                </div>

                                                <button
                                                    onClick={() => toggleExpanded(aposta.id)}
                                                    className="p-2 rounded-xl border-2 border-gray-200 hover:border-primary/50 transition-colors"
                                                    aria-label="Ver detalhes"
                                                >
                                                    <ChevronDown
                                                        size={18}
                                                        className={`transition-transform ${expanded ? 'rotate-180' : ''}`}
                                                    />
                                                </button>
                                            </div>

                                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">
                                                <div className="bg-gray-50 rounded-xl p-3">
                                                    <div className="text-xs font-semibold text-secondary">VALOR</div>
                                                    <div className="font-bold text-gray-900 mt-1">{toMoney(aposta.valorAposta)}</div>
                                                </div>
                                                <div className="bg-gray-50 rounded-xl p-3">
                                                    <div className="text-xs font-semibold text-secondary">RESULTADO</div>
                                                    <div className={`font-bold mt-1 ${meta.amountClass}`}>
                                                        {aposta.status === 'won'
                                                            ? `+${toMoney(aposta?.resultado?.premio || 0)}`
                                                            : aposta.status === 'lost'
                                                                ? `-${toMoney(aposta.valorAposta)}`
                                                                : 'Aguardando'}
                                                    </div>
                                                </div>
                                                <div className="bg-gray-50 rounded-xl p-3">
                                                    <div className="text-xs font-semibold text-secondary">APOSTA EM</div>
                                                    <div className="font-bold text-gray-900 mt-1">
                                                        {moment(aposta.created_at).format('DD/MM HH:mm')}
                                                    </div>
                                                </div>
                                                <div className="bg-gray-50 rounded-xl p-3">
                                                    <div className="text-xs font-semibold text-secondary">SORTEIO</div>
                                                    <div className="font-bold text-gray-900 mt-1">
                                                        {aposta?.sorteio?.data
                                                            ? moment(aposta.sorteio.data).format('DD/MM HH:mm')
                                                            : '-'}
                                                    </div>
                                                </div>
                                            </div>

                                            {expanded && (
                                                <div className="mt-4 pt-4 border-t border-gray-100">
                                                    <div className="text-sm font-bold text-gray-900 mb-2">Detalhes</div>

                                                    {aposta?.resultado?.resumo && (
                                                        <div className="bg-gradient-to-r from-blue-50 to-primary/10 rounded-2xl p-4 mb-3">
                                                            <div className="text-sm text-gray-700">
                                                                <div className="font-semibold mb-1">Resumo</div>
                                                                <div>{aposta.resultado.resumo}</div>
                                                            </div>
                                                        </div>
                                                    )}

                                                    <div className="space-y-2">
                                                        <div className="flex items-center justify-between text-sm">
                                                            <span className="text-secondary font-semibold">Modalidade</span>
                                                            <span className="font-bold text-gray-900">{aposta.modalidadeNome}</span>
                                                        </div>
                                                        {aposta.posicaoNome && (
                                                            <div className="flex items-center justify-between text-sm">
                                                                <span className="text-secondary font-semibold">Posição</span>
                                                                <span className="font-bold text-gray-900">{aposta.posicaoNome}</span>
                                                            </div>
                                                        )}
                                                        <div className="flex items-center justify-between text-sm">
                                                            <span className="text-secondary font-semibold">Palpites</span>
                                                            <span className="font-bold text-gray-900">{aposta?.palpites?.length || 0}</span>
                                                        </div>
                                                        {aposta?.resultado?.created_at && (
                                                            <div className="flex items-center justify-between text-sm">
                                                                <span className="text-secondary font-semibold">Resultado em</span>
                                                                <span className="font-bold text-gray-900">
                                                                    {moment(aposta.resultado.created_at).format('DD/MM HH:mm')}
                                                                </span>
                                                            </div>
                                                        )}
                                                    </div>

                                                    {Array.isArray(aposta?.palpites) && aposta.palpites.length > 0 && (
                                                        <div className="mt-4">
                                                            <div className="text-sm font-bold text-gray-900 mb-2">Seus palpites</div>
                                                            <div className="space-y-2">
                                                                {aposta.palpites.map((p, idx) => (
                                                                    <div
                                                                        key={`${aposta.id}-palpite-${idx}`}
                                                                        className="bg-white border-2 border-gray-200 rounded-xl p-3"
                                                                    >
                                                                        {Array.isArray(p?.numbers) ? (
                                                                            <div className="flex flex-wrap gap-1">
                                                                                {p.numbers.map((n) => (
                                                                                    <span
                                                                                        key={n}
                                                                                        className="inline-flex items-center justify-center w-8 h-8 bg-primary text-white rounded-md text-xs font-bold"
                                                                                    >
                                                                                        {n.toString().padStart(2, '0')}
                                                                                    </span>
                                                                                ))}
                                                                            </div>
                                                                        ) : (
                                                                            <span className="inline-flex items-center justify-center px-3 h-8 bg-primary text-white rounded-md text-xs font-bold tracking-widest">
                                                                                {(p?.display || '').toString()}
                                                                            </span>
                                                                        )}
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}

export default Historico;