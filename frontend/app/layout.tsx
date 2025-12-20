import type { Metadata } from "next";
import { Inter, Roboto_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import ThemeRegistry from "@/lib/theme/ThemeProvider";
import { StepperProvider } from "@/app/context";

const geistSans = Inter({
  subsets: ["latin"],
  variable: "--font-geist-sans",
});
const geistMono = Roboto_Mono({
  subsets: ["latin"],
  variable: "--font-geist-mono",
});

export const metadata: Metadata = {
  title: "AutoDealGenie - AI-Powered Automotive Deal Management",
  description:
    "Streamline your automotive deals with AI technology, real-time analytics, and intelligent automation.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ThemeRegistry>
          <ErrorBoundary>
            <AuthProvider>
              <StepperProvider>{children}</StepperProvider>
            </AuthProvider>
          </ErrorBoundary>
        </ThemeRegistry>
      </body>
    </html>
  );
}
