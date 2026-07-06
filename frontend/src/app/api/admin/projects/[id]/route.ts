import { NextResponse } from "next/server";

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
    const { id } = await context.params;

    const response =
      await fastApiAdminRequest(
        `/admin/projects/${id}`
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
      "Project detail proxy failed:",
      error
    );

    return NextResponse.json(
      {
        error:
          "Could not load project",
      },
      {
        status: 500,
      }
    );
  }
}