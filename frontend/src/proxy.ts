import {
  NextRequest,
  NextResponse,
} from "next/server";


const SESSION_COOKIE_NAME =
  "rateguard_session";


export function proxy(
  request: NextRequest
) {
  const token = request.cookies.get(
    SESSION_COOKIE_NAME
  )?.value;

  const pathname =
    request.nextUrl.pathname;

  const isDashboard =
    pathname.startsWith(
      "/dashboard"
    );

  const isAuthPage =
    pathname === "/login"
    || pathname === "/register";


  if (isDashboard && !token) {
    return NextResponse.redirect(
      new URL(
        "/login",
        request.url
      )
    );
  }


  if (isAuthPage && token) {
    return NextResponse.redirect(
      new URL(
        "/dashboard",
        request.url
      )
    );
  }


  return NextResponse.next();
}


export const config = {
  matcher: [
    "/dashboard/:path*",
    "/login",
    "/register",
  ],
};