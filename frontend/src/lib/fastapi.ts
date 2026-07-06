const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL;
const ADMIN_API_KEY = process.env.ADMIN_API_KEY;

if (!FASTAPI_BASE_URL) {
  throw new Error(
    "FASTAPI_BASE_URL environment variable is not configured"
  );
}

if (!ADMIN_API_KEY) {
  throw new Error(
    "ADMIN_API_KEY environment variable is not configured"
  );
}

type FastApiRequestOptions = {
  method?: string;
  body?: unknown;
};

export async function fastApiAdminRequest(
  path: string,
  options: FastApiRequestOptions = {}
): Promise<Response> {
  const headers = new Headers();

  headers.set(
    "x-admin-key",
    ADMIN_API_KEY
  );

  if (options.body !== undefined) {
    headers.set(
      "Content-Type",
      "application/json"
    );
  }

  return fetch(
    `${FASTAPI_BASE_URL}${path}`,
    {
      method: options.method ?? "GET",
      headers,
      body:
        options.body !== undefined
          ? JSON.stringify(options.body)
          : undefined,

      // Admin dashboard should receive fresh data.
      cache: "no-store",
    }
  );
}