"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  FormEvent,
  useState,
} from "react";


export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  async function handleSubmit(
    event: FormEvent
  ) {
    event.preventDefault();

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        "/api/auth/login",
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            email,
            password,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ??
          data.error ??
          "Could not log in"
        );
      }

      router.push("/dashboard");
      router.refresh();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not log in"
      );
    } finally {
      setLoading(false);
    }
  }


  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-4 py-10 text-white">
      <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-8 shadow-2xl shadow-black/20">

        <div className="mb-8">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-400">
            Developer-first rate limiting
          </p>

          <h1 className="mt-3 text-3xl font-bold leading-tight tracking-tight">
            Built for developers. Because your backend deserves boundaries.
          </h1>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Create projects, define custom endpoint limits, and protect your
            application with a simple server-to-server rate-limiting API.
          </p>
        </div>


        <div className="mb-6 border-t border-slate-800 pt-6">
          <p className="text-sm font-medium text-blue-400">
            RateGuard
          </p>

          <h2 className="mt-2 text-2xl font-bold">
            Welcome back
          </h2>

          <p className="mt-2 text-sm text-slate-400">
            Log in to manage your projects
            and rate limits.
          </p>
        </div>


        {error && (
          <div className="mb-5 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-400">
            {error}
          </div>
        )}


        <form
          onSubmit={handleSubmit}
          className="space-y-4"
        >
          <div>
            <label className="mb-2 block text-sm text-slate-300">
              Email
            </label>

            <input
              type="email"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              required
              placeholder="you@example.com"
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 outline-none transition focus:border-blue-500"
            />
          </div>


          <div>
            <label className="mb-2 block text-sm text-slate-300">
              Password
            </label>

            <input
              type="password"
              value={password}
              onChange={(event) =>
                setPassword(
                  event.target.value
                )
              }
              required
              placeholder="Your password"
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 outline-none transition focus:border-blue-500"
            />
          </div>


          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-blue-600 px-4 py-3 font-medium transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading
              ? "Logging in..."
              : "Log In"}
          </button>
        </form>


        <p className="mt-6 text-center text-sm text-slate-400">
          No account yet?{" "}

          <Link
            href="/register"
            className="font-medium text-blue-400 hover:text-blue-300"
          >
            Create one
          </Link>
        </p>
      </div>
    </main>
  );
}