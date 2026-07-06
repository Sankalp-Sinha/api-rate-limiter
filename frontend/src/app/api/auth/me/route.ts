import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import {
  getFastApiBaseUrl,
  SESSION_COOKIE_NAME,
} from "@/lib/server-auth";


export async function GET() {
  const cookieStore = await cookies();

  const token = cookieStore.get(
    SESSION_COOKIE_NAME
  )?.value;

  if (!token) {
    return NextResponse.json(
      {
        detail:
          "Authentication required",
      },
      {
        status: 401,
      }
    );
  }

  try {
    const response = await fetch(
      `${getFastApiBaseUrl()}/auth/me`,
      {
        headers: {
          Authorization:
            `Bearer ${token}`,
        },
        cache: "no-store",
      }
    );

    const data = await response.json();

    return NextResponse.json(
      data,
      {
        status: response.status,
      }
    );
  } catch (error) {
    console.error(
      "Current user request failed:",
      error
    );

    return NextResponse.json(
      {
        error:
          "Could not verify session",
      },
      {
        status: 500,
      }
    );
  }
}