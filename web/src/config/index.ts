interface Config {
  apiBaseUrl: string;
}

const config: Config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL
}

export default config 