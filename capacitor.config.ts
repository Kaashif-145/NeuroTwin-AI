import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'ai.neurotwin.platform',
  appName: 'NeuroTwin AI',
  webDir: 'www',
  server: {
    // CHANGE THIS to your hosted Streamlit URL (e.g. https://your-app.streamlit.app)
    url: 'https://neurotwin-ai.streamlit.app',
    cleartext: true
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 3000,
      backgroundColor: "#0E1117",
      showSpinner: true,
      androidScaleType: "CENTER_CROP",
      splashFullScreen: true,
      splashImmersive: true,
    }
  }
};

export default config;
