'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { StatCard } from '@/components/StatCard';
import { BookmarkCard } from '@/components/BookmarkCard';
import { BookmarkWithAnalysis } from '@/lib/data';

interface OverviewClientProps {
  initialStats: {
    total: number;
    test_this_week: number;
    build_later: number;
    archive: number;
    ignore: number;
  };
  initialBookmarks: BookmarkWithAnalysis[];
}

export default function OverviewClient({ initialStats, initialBookmarks }: OverviewClientProps) {
  const [stats, setStats] = useState(initialStats);
  const [bookmarks, setBookmarks] = useState(initialBookmarks);
  const [loading, setLoading] = useState(false);

  // Client-side: Fetch fresh data on mount and every 30 seconds
  useEffect(() => {
    async function fetchFreshData() {
      try {
        setLoading(true);
        const [bookmarksRes, analysisRes] = await Promise.all([
          fetch('/data.json?t=' + Date.now()),
          fetch('/analysis.json?t=' + Date.now())
        ]);
        
        if (!bookmarksRes.ok || !analysisRes.ok) {
          throw new Error('Failed to fetch');
        }
        
        const bookmarksData = await bookmarksRes.json();
        const analysisData = await analysisRes.json();
        
        // Merge data
        const analysisMap = new Map(analysisData.map((a: any) => [a.bookmark_id, a]));
        const merged = bookmarksData.map((b: any) => ({
          ...b,
          analysis: analysisMap.get(b.id) || null,
        }));
        
        // Sort by bookmarked_at desc
        merged.sort((a: any, b: any) => 
          new Date(b.bookmarked_at).getTime() - new Date(a.bookmarked_at).getTime()
        );
        
        setBookmarks(merged.slice(0, 10));
        
        // Update stats
        const withAnalysis = merged.filter((b: any) => b.analysis);
        setStats({
          total: merged.length,
          test_this_week: withAnalysis.filter((b: any) => b.analysis?.recommendation_bucket === 'test_this_week').length,
          build_later: withAnalysis.filter((b: any) => b.analysis?.recommendation_bucket === 'build_later').length,
          archive: withAnalysis.filter((b: any) => b.analysis?.recommendation_bucket === 'archive').length,
          ignore: withAnalysis.filter((b: any) => b.analysis?.recommendation_bucket === 'ignore').length,
        });
      } catch (err) {
        console.error('Failed to fetch fresh data:', err);
        // Keep initial data on error
      } finally {
        setLoading(false);
      }
    }

    // Fetch immediately
    fetchFreshData();
    
    // Then every 30 seconds
    const interval = setInterval(fetchFreshData, 30000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      <section>
        <h2 className="section-title" style={{ marginBottom: '16px' }}>
          Dashboard {loading && <span style={{ fontSize: '0.75rem', color: '#888' }}>(syncing...)</span>}
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
        
        <div className="bookmark-list">
          {bookmarks.length > 0 ? (
            bookmarks.map((bookmark) => (
              <BookmarkCard key={bookmark.id} bookmark={bookmark} />
            ))
          ) : (
            <div className="empty-state">
              <p>No bookmarks yet.</p>
              <p style={{ fontSize: '0.875rem', marginTop: '8px' }}>
                Save your first bookmark to see it here.
              </p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
