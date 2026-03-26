'use client';

import { useState, useMemo } from 'react';
import Link from 'next/link';
import { StatCard } from '@/components/StatCard';
import { BookmarkCard } from '@/components/BookmarkCard';
import { SearchBar } from '@/components/SearchBar';
import { getStats, getBookmarksWithAnalysis } from '@/lib/data';

// ISR: Rebuild every 60 seconds  
export const revalidate = 60;

export default function OverviewPage() {
  const stats = getStats();
  const allBookmarks = getBookmarksWithAnalysis();
  const [searchQuery, setSearchQuery] = useState('');
  
  // Filter bookmarks by search
  const filteredBookmarks = useMemo(() => {
    let bookmarks = allBookmarks;
    
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      bookmarks = bookmarks.filter(bookmark => {
        const searchableText = `
          ${bookmark.title} 
          ${bookmark.text} 
          ${bookmark.author || ''} 
          ${bookmark.analysis?.summary || ''}
          ${bookmark.analysis?.recommendation_reason || ''}
          ${bookmark.analysis?.key_insights?.join(' ') || ''}
          ${bookmark.tags?.join(' ') || ''}
        `.toLowerCase();
        
        return searchableText.includes(query);
      });
    }
    
    // Sort by bookmarked_at desc and take top 10
    return bookmarks
      .sort((a, b) => new Date(b.bookmarked_at).getTime() - new Date(a.bookmarked_at).getTime())
      .slice(0, 10);
  }, [allBookmarks, searchQuery]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      <section>
        <h2 className="section-title" style={{ marginBottom: '16px' }}>
          Dashboard
        </h2>
        <div className="stats-grid">
          <StatCard label="Total Bookmarks" value={stats.total} color="gray" />
          <StatCard label="Test This Week" value={stats.test_this_week} color="green" />
          <StatCard label="Build Later" value={stats.build_later} color="orange" />
          <StatCard label="Archive" value={stats.archive} color="gray" />
        </div>
      </section>

      <section>
        <div className="section-header">
          <h2 className="section-title">Recent Bookmarks</h2>
          <Link href="/bookmarks" className="view-all">
            View all →
          </Link>
        </div>
        
        <SearchBar 
          value={searchQuery} 
          onChange={setSearchQuery}
          placeholder="Search your bookmarks..."
        />
        <div className="bookmark-list">
          {filteredBookmarks.length > 0 ? (
            filteredBookmarks.map((bookmark) => (
              <BookmarkCard key={bookmark.id} bookmark={bookmark} />
            ))
          ) : (
            <div className="empty-state">
              <p>No bookmarks found.</p>
              {searchQuery && <p style={{ fontSize: '0.875rem', marginTop: '8px' }}>Try a different search term.</p>}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
