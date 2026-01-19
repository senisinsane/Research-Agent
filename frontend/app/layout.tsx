import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Web Research Agent | AG-UI",
  description: "Autonomous web research agent powered by AG-UI Protocol",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
