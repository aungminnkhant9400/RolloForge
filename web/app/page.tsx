import { getStats, getRecentBookmarks } from '@/lib/data';
import OverviewClient from './OverviewClient';

// ISR: Rebuild every 60 seconds
export const revalidate = 60;

export default function OverviewPage() {
  const stats = getStats();
  const recentBookmarks = getRecentBookmarks(10);

  return (
    <OverviewClient 
      initialStats={stats} 
      initialBookmarks={recentBookmarks} 
    />
  );
}
// Force deploy 1774461918
