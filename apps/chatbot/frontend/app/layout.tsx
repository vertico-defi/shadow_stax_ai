import "../styles/globals.css";
import type { ReactNode } from "react";
import { branding } from "../lib/branding";

export const metadata = {
  title: branding.productName,
  description: branding.tagline
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-neutral-950 text-neutral-100">
        {children}
      </body>
    </html>
  );
}
