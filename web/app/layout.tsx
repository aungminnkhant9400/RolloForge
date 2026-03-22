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
      <body className="min-h-screen bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {/* Header */}
          <header className="mb-8">
            <h1 className="text-3xl sm:text-4xl font-bold text-ink mb-2">
              RolloForge
            </h1>
            <p className="text-muted">
              Bookmark intelligence for AI agents
            </p>
          </header>
          
          {/* Navigation Tabs */}
          <LayoutTabs />
          
          {/* Main Content */}
          <main className="mt-6">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}