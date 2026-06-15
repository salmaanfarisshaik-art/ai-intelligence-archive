const fs = require('fs');
const path = require('path');

function copyRecursiveSync(src, dest) {
  const exists = fs.existsSync(src);
  const stats = exists && fs.statSync(src);
  const isDirectory = exists && stats.isDirectory();
  if (isDirectory) {
    if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true });
    fs.readdirSync(src).forEach(childItemName => {
      copyRecursiveSync(path.join(src, childItemName), path.join(dest, childItemName));
    });
  } else {
    // Only copy if it's not a directory
    if (!fs.existsSync(path.dirname(dest))) fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.copyFileSync(src, dest);
  }
}

const siteDir = path.join(__dirname, '..', 'site');
const publicSiteDir = path.join(__dirname, 'public', 'site');

console.log(`Copying data from ${siteDir} to ${publicSiteDir}`);
if (fs.existsSync(siteDir)) {
  copyRecursiveSync(siteDir, publicSiteDir);
  console.log('Copy complete.');
} else {
  console.log('Site directory not found. Skipping.');
}
