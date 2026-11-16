import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/authContext";
import { ThemeProvider } from "@/lib/themeContext";
import { NavigationProvider } from "@/lib/navigationContext";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { SavedItemsDrawer } from "@/components/SavedItemsDrawer";
import { BRAND } from "@/lib/brandConfig";

export const metadata: Metadata = {
  title: `${BRAND.name} — ${BRAND.tagline}`,
  description: "Connect architectural inspiration to verified manufacturers, products, and regional supply vendors across India and global craft hubs.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var k='${BRAND.themeStorageKey}';var t=localStorage.getItem(k)||localStorage.getItem('materiq_theme');var p=window.matchMedia('(prefers-color-scheme: dark)').matches;if(t==='dark'||(!t&&p)){document.documentElement.classList.add('dark');document.documentElement.setAttribute('data-theme','dark');document.documentElement.style.colorScheme='dark';}else{document.documentElement.classList.remove('dark');document.documentElement.setAttribute('data-theme','light');document.documentElement.style.colorScheme='light';}}catch(e){}})();`,
          }}
        />
      </head>
      <body className="min-h-screen flex flex-col bg-arch-bg text-arch-charcoal dark:bg-arch-dark-bg dark:text-arch-dark-text antialiased selection:bg-arch-terracotta/20 selection:text-arch-terracotta transition-colors duration-200">
        <ThemeProvider>
          <AuthProvider>
            <NavigationProvider>
              <Navbar />
              <main className="flex-grow w-full">
                {children}
              </main>
              <Footer />
              <SavedItemsDrawer />
            </NavigationProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
