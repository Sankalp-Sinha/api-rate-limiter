import { NextResponse } from "next/server";

import { fastApiAdminRequest } from "@/lib/fastapi";


type RouteContext = {
  params: Promise<{
    id: string;
  }>;
};


export async function POST(
  _request: Request,
  context: RouteContext
) {
  try {
    const { id } = await context.params;

    const response = await fastApiAdminRequest(
      `/admin/api-keys/${id}/revoke`,
      {
        method: "POST",
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
      "API key revoke proxy failed:",
      error
    );

    return NextResponse.json(
      {
        error: "Could not revoke API key",
      },
      {
        status: 500,
      }
    );
  }
}