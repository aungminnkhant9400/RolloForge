'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { StatCard } from '@/components/StatCard';
import { BookmarkCard } from '@/components/BookmarkCard';

export default function OverviewPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch('/api/data');
        if (!response.ok) throw new Error('Failed to fetch');
        const json = await response.json();
        setData(json);
      } catch (err) {
        setError(err.message);
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
  if (error) return <div style={{ padding: '2rem', color: 'red' }}>Error: {error}</div>;
  if (!data) return null;

  const { stats, bookmarks } = data;
  const recentBookmarks = bookmarks.slice(0, 10);

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
          {recentBookmarks.length > 0 ? (
            recentBookmarks.map((bookmark) => (
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
