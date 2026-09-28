import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  reporter: 'list',
  use: { baseURL: 'http://localhost:8081', browserName: 'chromium', viewport: { width: 390, height: 844 } },
  webServer: { command: 'npx --yes serve -l 8081 .', url: 'http://localhost:8081', reuseExistingServer: true }
});
