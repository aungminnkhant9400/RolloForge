'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, BookOpen, Settings } from 'lucide-react';

const tabs = [
  { href: '/', label: 'Overview', icon: Home },
  { href: '/bookmarks', label: 'Bookmarks', icon: BookOpen },
];

export function LayoutTabs() {
  const pathname = usePathname();
  
  return (
    <nav className="border-b border-line">
      <ul className="flex gap-1">
        {tabs.map((tab) => {
          const isActive = pathname === tab.href;
          const Icon = tab.icon;
          
          return (
            <li key={tab.href}>
              <Link
                href={tab.href}
                className={`
                  flex items-center gap-2 px-4 py-3 rounded-t-lg
                  transition-colors duration-200
                  ${isActive 
                    ? 'bg-panel text-accent border-b-2 border-accent font-medium' 
                    : 'text-muted hover:text-ink hover:bg-panel/50'}
                `}
              >
                <Icon size={18} />
                <span className="hidden sm:inline">{tab.label}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}