import { NextResponse } from "next/server";

import { fastApiAdminRequest } from "@/lib/fastapi";


export async function GET() {
  try {
    const response = await fastApiAdminRequest(
      "/admin/plans"
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
      "Plan list proxy failed:",
      error
    );

    return NextResponse.json(
      {
        error: "Could not load plans",
      },
      {
        status: 500,
      }
    );
  }
}