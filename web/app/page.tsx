import { StatCard } from '@/components/StatCard';
import { BookmarkCard } from '@/components/BookmarkCard';
import { getStats, getRecentBookmarks } from '@/lib/data';
import Link from 'next/link';

// ISR: Rebuild every 60 seconds  
export const revalidate = 60;

export default function OverviewPage() {
  const stats = getStats();
  const recentBookmarks = getRecentBookmarks(10);

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
