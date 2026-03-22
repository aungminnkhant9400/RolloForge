'use client';

import { Search } from 'lucide-react';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export function SearchBar({ value, onChange, placeholder = 'Search bookmarks...' }: SearchBarProps) {
  return (
    <div className="relative">
      <Search 
        size={18} 
        className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" 
      />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="
          w-full pl-10 pr-4 py-3
          bg-panel border border-line rounded-xl
          text-ink placeholder:text-muted
          focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent
          transition-all
        "
      />
    </div>
  );
}