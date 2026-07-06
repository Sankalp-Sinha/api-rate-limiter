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
  }>;
};


export async function GET(
  request: NextRequest,
  context: RouteContext
) {
  try {
    const { id } =
      await context.params;

    const hours =
      request.nextUrl.searchParams.get(
        "hours"
      ) ?? "24";

    const response =
      await fastApiAdminRequest(
        `/admin/projects/${id}/analytics/summary?hours=${encodeURIComponent(hours)}`
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
      "Project analytics summary proxy failed:",
      error
    );

    return NextResponse.json(
      {
        error:
          "Could not load project analytics",
      },
      {
        status: 500,
      }
    );
  }
}