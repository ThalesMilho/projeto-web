import Pusher from "pusher-js";
import Echo from "laravel-echo";

export default class SocketServiceBase {
    user_id;

    conectarWebSocket(authToken, user_id, ContextoUsuario = null) {
        window.Pusher = Pusher;
        this.user_id = user_id;

        const key = process.env.NEXT_PUBLIC_PUSHER_KEY || "fjnwxlbq15yngixkkcgf";
        const wsHost = process.env.NEXT_PUBLIC_WS_HOST || "ws.salapix.com.br";
        const authEndpoint =
            process.env.NEXT_PUBLIC_AUTH_ENDPOINT ||
            "https://api.salapix.com.br/api/websocket";
        const wsPort =
            process.env.NEXT_PUBLIC_WS_PORT && process.env.NEXT_PUBLIC_WS_PORT !== "null"
                ? parseInt(process.env.NEXT_PUBLIC_WS_PORT)
                : null;
        const wssPort =
            process.env.NEXT_PUBLIC_WSS_PORT && process.env.NEXT_PUBLIC_WSS_PORT !== "null"
                ? parseInt(process.env.NEXT_PUBLIC_WSS_PORT)
                : null;
        const forceTLS =
            process.env.NEXT_PUBLIC_FORCE_TLS !== undefined
                ? process.env.NEXT_PUBLIC_FORCE_TLS === "true"
                : false;

        window.Echo = new Echo({
            broadcaster: "reverb",
            key,
            wsHost,
            authEndpoint,
            wsPort,
            wssPort,
            forceTLS,
            enabledTransports: ["ws", "wss"],
            auth: {
                headers: {
                    Authorization: `Bearer ${authToken}`,
                },
            },
        });
    }
}
