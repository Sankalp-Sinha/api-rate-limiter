import { NextRequest, NextResponse } from "next/server";

import { fastApiAdminRequest } from "@/lib/fastapi";


export async function GET() {
  try {
    const response = await fastApiAdminRequest(
      "/admin/api-keys"
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
      "API key list proxy failed:",
      error
    );

    return NextResponse.json(
      {
        error: "Could not load API keys",
      },
      {
        status: 500,
      }
    );
  }
}


export async function POST(
  request: NextRequest
) {
  try {
    const body = await request.json();

    const response = await fastApiAdminRequest(
      "/admin/api-keys",
      {
        method: "POST",
        body,
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
      "API key creation proxy failed:",
      error
    );

    return NextResponse.json(
      {
        error: "Could not create API key",
      },
      {
        status: 500,
      }
    );
  }
}