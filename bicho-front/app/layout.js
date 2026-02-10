import localFont from "next/font/local";
import "./globals.css";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata = {
  title: "Maior Bicho",
  description: "Ganhe dinheiro em poucos minutos",
};

export default function RootLayout({ children }) {
  return (
      <html lang="pt">
      <meta name="theme-color" content="#3C7FFF" id="theme-color"/>
      <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"/>
      <body
          className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
      {children}
      </body>
      </html>
  );
}
