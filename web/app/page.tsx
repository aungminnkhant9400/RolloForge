import { StatCard } from '@/components/StatCard';
import { BookmarkCard } from '@/components/BookmarkCard';
import { getStats, getRecentBookmarks } from '@/lib/data';

export default function OverviewPage() {
  const stats = getStats();
  const recentBookmarks = getRecentBookmarks(5);

  return (
    <div className="space-y-8">
      {/* Stats Grid */}
      <section>
        <h2 className="text-xl font-semibold text-ink mb-4">Dashboard</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard 
            label="Total Bookmarks" 
            value={stats.total} 
            color="gray" 
          />
          <StatCard 
            label="Test This Week" 
            value={stats.test_this_week} 
            color="green" 
          />
          <StatCard 
            label="Build Later" 
            value={stats.build_later} 
            color="orange" 
          />
          <StatCard 
            label="Archive" 
            value={stats.archive} 
            color="gray" 
          />
        </div>
      </section>

      {/* Recent Bookmarks */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-ink">Recent Bookmarks</h2>
          <a 
            href="/bookmarks" 
            className="text-accent hover:text-accent-soft transition-colors"
          >
            View all →
          </a>
        </div>
        
        <div className="grid gap-4">
          {recentBookmarks.length > 0 ? (
            recentBookmarks.map((bookmark) => (
              <BookmarkCard 
                key={bookmark.id} 
                bookmark={bookmark} 
              />
            ))
          ) : (
            <div className="text-center py-12 text-muted bg-panel rounded-2xl border border-line">
              <p>No bookmarks yet.</p>
              <p className="text-sm mt-2">Save your first bookmark to see it here.</p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}