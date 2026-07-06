"use client";

import { LogOut } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";


export default function LogoutButton() {
  const router = useRouter();

  const [loading, setLoading] =
    useState(false);


  async function logout() {
    try {
      setLoading(true);

      await fetch(
        "/api/auth/logout",
        {
          method: "POST",
        }
      );

      router.push("/login");
      router.refresh();
    } finally {
      setLoading(false);
    }
  }


  return (
    <button
      onClick={() => void logout()}
      disabled={loading}
      className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-slate-400 transition hover:bg-slate-800 hover:text-white disabled:opacity-50"
    >
      <LogOut size={18} />

      {loading
        ? "Logging out..."
        : "Log out"}
    </button>
  );
}