const fs = require('fs');
const path = require('path');

// Go up 2 levels: web/lib/ -> web/ -> repo root
const dataDir = path.join(__dirname, '..', '..', 'data');
const libDir = __dirname;

try {
  // Copy bookmarks
  const bookmarksSrc = path.join(dataDir, 'bookmarks_raw.json');
  const bookmarksDest = path.join(libDir, 'data.json');
  
  if (fs.existsSync(bookmarksSrc)) {
    fs.copyFileSync(bookmarksSrc, bookmarksDest);
    console.log('✓ Copied bookmarks_raw.json');
  } else {
    fs.writeFileSync(bookmarksDest, '[]');
    console.log('✓ Created empty data.json');
  }
  
  // Copy analysis
  const analysisSrc = path.join(dataDir, 'analysis_results.json');
  const analysisDest = path.join(libDir, 'analysis.json');
  
  if (fs.existsSync(analysisSrc)) {
    fs.copyFileSync(analysisSrc, analysisDest);
    console.log('✓ Copied analysis_results.json');
  } else {
    fs.writeFileSync(analysisDest, '[]');
    console.log('✓ Created empty analysis.json');
  }
  
} catch (err) {
  console.error('Error copying data:', err);
  process.exit(1);
}