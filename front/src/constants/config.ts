const forceExtBackend = true

export const config = {
  isDemo: false,
  apiUrl: (import.meta.env.PROD || forceExtBackend) ? 'https://fullstack-api.bazzled.com' : 'http://localhost:8000',
}