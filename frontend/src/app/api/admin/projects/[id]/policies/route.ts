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
  _request: Request,
  context: RouteContext
) {
  try {
    const { id } =
      await context.params;

    const response =
      await fastApiAdminRequest(
        `/admin/projects/${id}/policies`
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
      "Policy list proxy failed:",
      error
    );

    return NextResponse.json(
      {
        error:
          "Could not load policies",
      },
      {
        status: 500,
      }
    );
  }
}


export async function POST(
  request: NextRequest,
  context: RouteContext
) {
  try {
    const { id } =
      await context.params;

    const body =
      await request.json();

    const response =
      await fastApiAdminRequest(
        `/admin/projects/${id}/policies`,
        {
          method: "POST",
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
      "Policy creation proxy failed:",
      error
    );

    return NextResponse.json(
      {
        error:
          "Could not create policy",
      },
      {
        status: 500,
      }
    );
  }
}