import { NextResponse } from "next/server";

import {
  fastApiAdminRequest,
} from "@/lib/fastapi";


type RouteContext = {
  params: Promise<{
    id: string;
    keyId: string;
  }>;
};


export async function POST(
  _request: Request,
  context: RouteContext
) {
  try {
    const {
      id,
      keyId,
    } = await context.params;

    const response =
      await fastApiAdminRequest(
        `/admin/projects/${id}/api-keys/${keyId}/revoke`,
        {
          method: "POST",
        }
      );

    const data =
      await response.json();

    return NextResponse.json(
      data,
      {
        status: response.status,
      }
    );
  } catch (error) {
    console.error(
      "Project API key revoke proxy failed:",
      error
    );

    return NextResponse.json(
      {
        error:
          "Could not revoke project API key",
      },
      {
        status: 500,
      }
    );
  }
}