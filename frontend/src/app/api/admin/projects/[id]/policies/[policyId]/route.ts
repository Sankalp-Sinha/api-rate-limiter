import {
  NextRequest,
  NextResponse,
} from "next/server";

import {
  fastApiAdminRequest,
} from "@/lib/fastapi";


type RouteContext = {
  params: Promise<{
    id: string;
    policyId: string;
  }>;
};


export async function PUT(
  request: NextRequest,
  context: RouteContext
) {
  try {
    const {
      id,
      policyId,
    } = await context.params;

    const body =
      await request.json();

    const response =
      await fastApiAdminRequest(
        `/admin/projects/${id}/policies/${policyId}`,
        {
          method: "PUT",
          body,
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
      "Policy update proxy failed:",
      error
    );

    return NextResponse.json(
      {
        error:
          "Could not update policy",
      },
      {
        status: 500,
      }
    );
  }
}