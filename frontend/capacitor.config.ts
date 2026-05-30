import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.drivelegal.app',
  appName: 'DriveLegal',
  webDir: 'dist',
  server: {
    androidScheme: 'https',
  },
  android: {
    allowMixedContent: true, // required because backend is HTTP (not HTTPS)
  },
};

export default config;
