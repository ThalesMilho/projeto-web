// middleware.js
import { NextResponse } from 'next/server';

export function middleware(request) {
    const token = request.cookies.get('authToken');

    // Verificar se o token é válido
    // if (!token && !request.nextUrl.pathname.toString().startsWith('/app/sala/') && request.nextUrl.pathname != "/app/jogos") {
    //     return NextResponse.redirect(new URL('/login', request.url));
    // }

    // Lógica para verificar o token (ex: usando um serviço de autenticação)

    return NextResponse.next();
}

export const config = {
    matcher: ['/app/:path*'], // Aplicar o middleware apenas em rotas protegidas
};