import { NextResponse } from "next/server";

import {
  fastApiAdminRequest,
} from "@/lib/fastapi";


type RouteContext = {
  params: Promise<{
    id: string;
    policyId: string;
  }>;
};


export async function POST(
  _request: Request,
  context: RouteContext
) {
  try {
    const {
      id,
      policyId,
    } = await context.params;

    const response =
      await fastApiAdminRequest(
        `/admin/projects/${id}/policies/${policyId}/deactivate`,
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
      "Policy deactivate proxy failed:",
      error
    );

    return NextResponse.json(
      {
        error:
          "Could not deactivate policy",
      },
      {
        status: 500,
      }
    );
  }
}