import "server-only";

import { cookies } from "next/headers";

import {
  SESSION_COOKIE_NAME,
} from "@/lib/server-auth";


function requireEnv(
  value: string | undefined,
  name: string
): string {
  if (!value) {
    throw new Error(
      `${name} is not configured`
    );
  }

  return value;
}


const FASTAPI_BASE_URL: string =
  requireEnv(
    process.env.FASTAPI_BASE_URL,
    "FASTAPI_BASE_URL"
  );


const ADMIN_API_KEY: string =
  requireEnv(
    process.env.ADMIN_API_KEY,
    "ADMIN_API_KEY"
  );


type FastApiRequestOptions = {
  method?: string;
  body?: unknown;
};


function authenticationRequiredResponse():
  Response {
  return new Response(
    JSON.stringify({
      detail:
        "Authentication required",
    }),
    {
      status: 401,
      headers: {
        "Content-Type":
          "application/json",
      },
    }
  );
}


export async function fastApiAdminRequest(
  path: string,
  options: FastApiRequestOptions = {}
): Promise<Response> {
  const cookieStore = await cookies();

  const accessToken = cookieStore.get(
    SESSION_COOKIE_NAME
  )?.value;

  if (!accessToken) {
    return authenticationRequiredResponse();
  }

  const headers = new Headers();

  headers.set(
    "x-admin-key",
    ADMIN_API_KEY
  );

  headers.set(
    "Authorization",
    `Bearer ${accessToken}`
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
      method:
        options.method ?? "GET",

      headers,

      body:
        options.body !== undefined
          ? JSON.stringify(
              options.body
            )
          : undefined,

      cache: "no-store",
    }
  );
}