import { getBookmarksWithAnalysis, getAllTags, getStats } from '@/lib/data';

export default function handler(req, res) {
  try {
    const bookmarks = getBookmarksWithAnalysis();
    const tags = getAllTags();
    const stats = getStats();
    
    res.status(200).json({
      bookmarks,
      tags,
      stats,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
