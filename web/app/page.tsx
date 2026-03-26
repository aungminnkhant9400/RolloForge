'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { StatCard } from '@/components/StatCard';
import { BookmarkCard } from '@/components/BookmarkCard';

export default function OverviewPage() {
  const [bookmarks, setBookmarks] = useState([]);
  const [stats, setStats] = useState({ total: 0, test_this_week: 0, build_later: 0, archive: 0, ignore: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        // Fetch directly from static files with cache-busting
        // Aggressive cache busting
        const cacheBuster = `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const [bookmarksRes, analysisRes] = await Promise.all([
          fetch(`/data.json?cb=${cacheBuster}`, { cache: 'no-store' }),
          fetch(`/analysis.json?cb=${cacheBuster}`, { cache: 'no-store' })
        ]);
        
        if (!bookmarksRes.ok || !analysisRes.ok) {
          throw new Error('Failed to fetch data');
        }
        
        const bookmarksData = await bookmarksRes.json();
        const analysisData = await analysisRes.json();
        
        // Merge data
        const analysisMap = new Map(analysisData.map(a => [a.bookmark_id, a]));
        const merged = bookmarksData.map(b => ({
          ...b,
          analysis: analysisMap.get(b.id) || null,
        }));
        
        // Sort by bookmarked_at desc
        merged.sort((a, b) => new Date(b.bookmarked_at) - new Date(a.bookmarked_at));
        
        setBookmarks(merged.slice(0, 10));
        
        // Calculate stats
        const withAnalysis = merged.filter(b => b.analysis);
        setStats({
          total: merged.length,
          test_this_week: withAnalysis.filter(b => b.analysis?.recommendation_bucket === 'test_this_week').length,
          build_later: withAnalysis.filter(b => b.analysis?.recommendation_bucket === 'build_later').length,
          archive: withAnalysis.filter(b => b.analysis?.recommendation_bucket === 'archive').length,
          ignore: withAnalysis.filter(b => b.analysis?.recommendation_bucket === 'ignore').length,
        });
      } catch (err) {
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
    // Refresh every 10 seconds
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div style={{ padding: '2rem' }}>Loading...</div>;

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
        
        <div className="bookmark-list">
          {bookmarks.length > 0 ? (
            bookmarks.map((bookmark) => (
              <BookmarkCard key={bookmark.id} bookmark={bookmark} />
            ))
          ) : (
            <div className="empty-state">
              <p>No bookmarks yet.</p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
