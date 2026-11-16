// AIK Studio — browser tests. Static site: Playwright serves aik-site/ itself.
//   npm test                      all checks
//   npm run test:visual           screenshots only (tests/output/)
// Generated media (media/flight, built by tools/build-flight-media.sh) and the
// original logo files must be present for a clean run. Where they cannot be
// (a machine without the Higgsfield CDN), AIK_MEDIA_OPTIONAL=1 tolerates
// exactly those missing files and nothing else; AIK_MEDIA_OPTIONAL=logo
// tolerates only the original logo files (film present).
import { defineConfig } from '@playwright/test';

const exe = process.env.CHROMIUM_PATH || undefined;   // e.g. /opt/pw-browsers/chromium-1194/chrome-linux/chrome

export default defineConfig({
  testDir: './tests',
  outputDir: './test-results',
  timeout: 60_000,
  fullyParallel: true,
  reporter: [['list']],
  use: {
    baseURL: 'http://localhost:8765',
    launchOptions: exe ? { executablePath: exe } : {},
  },
  webServer: {
    command: 'python3 -m http.server 8765',
    url: 'http://localhost:8765/',
    reuseExistingServer: true,
    stdout: 'ignore',
    stderr: 'ignore',
  },
});
