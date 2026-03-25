/** @type {import('next').NextConfig} */
const nextConfig = {
  // Removed output: 'export' - now using SSR
  images: {
    unoptimized: true
  },
}

module.exports = nextConfig
