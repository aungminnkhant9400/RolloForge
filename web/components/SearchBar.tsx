'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { Search } from 'lucide-react';
import { useState, useEffect } from 'react';

interface SearchBarProps {
  initialValue?: string;
}

export function SearchBar({ initialValue = '' }: SearchBarProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [value, setValue] = useState(initialValue);

  useEffect(() => {
    setValue(initialValue);
  }, [initialValue]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams(searchParams.toString());
    if (value.trim()) {
      params.set('q', value.trim());
    } else {
      params.delete('q');
    }
    router.push(`/bookmarks?${params.toString()}`);
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <Search 
        size={18} 
        className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" 
      />
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Search bookmarks..."
        className="
          w-full pl-10 pr-4 py-3
          bg-panel border border-line rounded-xl
          text-ink placeholder:text-muted
          focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent
          transition-all
        "
      />
    </form>
  );
}