import {
  NextRequest,
  NextResponse,
} from "next/server";

import {
  fastApiAdminRequest,
} from "@/lib/fastapi";


export async function GET() {
  try {
    const response =
      await fastApiAdminRequest(
        "/admin/projects"
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
      "Project list proxy failed:",
      error
    );

    return NextResponse.json(
      {
        error:
          "Could not load projects",
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
    const body =
      await request.json();

    const response =
      await fastApiAdminRequest(
        "/admin/projects",
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
      "Project creation proxy failed:",
      error
    );

    return NextResponse.json(
      {
        error:
          "Could not create project",
      },
      {
        status: 500,
      }
    );
  }
}