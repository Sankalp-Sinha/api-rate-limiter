import {
  NextRequest,
  NextResponse,
} from "next/server";

import {
  getFastApiBaseUrl,
  SESSION_COOKIE_NAME,
} from "@/lib/server-auth";


export async function POST(
  request: NextRequest
) {
  try {
    const body = await request.json();

    const response = await fetch(
      `${getFastApiBaseUrl()}/auth/login`,
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify(body),
        cache: "no-store",
      }
    );

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        data,
        {
          status: response.status,
        }
      );
    }

    const nextResponse =
      NextResponse.json({
        user: data.user,
      });

    nextResponse.cookies.set(
      SESSION_COOKIE_NAME,
      data.access_token,
      {
        httpOnly: true,
        secure:
          process.env.NODE_ENV
          === "production",
        sameSite: "lax",
        path: "/",
        maxAge: data.expires_in,
      }
    );

    return nextResponse;
  } catch (error) {
    console.error(
      "Login proxy failed:",
      error
    );

    return NextResponse.json(
      {
        error: "Could not log in",
      },
      {
        status: 500,
      }
    );
  }
}