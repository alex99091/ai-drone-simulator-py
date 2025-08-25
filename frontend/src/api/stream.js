const HTTP_BASE = import.meta.env.VITE_BACKEND_HTTP
export function getVideoUrl() { return `${HTTP_BASE}/video` }
