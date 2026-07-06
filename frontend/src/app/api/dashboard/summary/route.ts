import { NextResponse } from "next/server";

import { fastApiAdminRequest } from "@/lib/fastapi";


export async function GET() {
  try {
    const response = await fastApiAdminRequest(
      "/admin/analytics/summary?hours=24"
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
      "Dashboard summary proxy failed:",
      error
    );

    return NextResponse.json(
      {
        error: "Could not load dashboard summary",
      },
      {
        status: 500,
      }
    );
  }
}