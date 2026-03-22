import type { Metadata } from 'next';
import './globals.css';
import { LayoutTabs } from '@/components/LayoutTabs';

export const metadata: Metadata = {
  title: 'RolloForge Dashboard',
  description: 'Bookmark intelligence for AI agents',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="container">
          <header className="header">
            <h1>RolloForge</h1>
            <p>Bookmark intelligence for AI agents</p>
          </header>
          <LayoutTabs />
          <main>{children}</main>
        </div>
      </body>
    </html>
  );
}