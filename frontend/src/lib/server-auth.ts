import "server-only";


export const SESSION_COOKIE_NAME =
  "rateguard_session";


export function getFastApiBaseUrl() {
  const baseUrl =
    process.env.FASTAPI_BASE_URL;

  if (!baseUrl) {
    throw new Error(
      "FASTAPI_BASE_URL is not configured"
    );
  }

  return baseUrl;
}