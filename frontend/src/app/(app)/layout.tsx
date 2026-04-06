/**
 * App layout with sidebar navigation.
 * Wraps Chat, Dashboard, Journey, Weekly Report, and Profile pages.
 * On mobile (<md) the sidebar collapses behind a hamburger toggle.
 */

"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { clsx } from "clsx";
import { LayoutDashboard, MessageSquare, User, LogOut, TrendingUp, ClipboardList, Menu, X } from "lucide-react";
import { isAuthenticated, logoutUser } from "@/lib/auth";
import { CalmModeSidebar } from "@/components/wellness/CalmModeSidebar";

const NAV_ITEMS = [
  { href: "/chat", label: "Chat", icon: MessageSquare },
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/journey", label: "Journey", icon: TrendingUp },
  { href: "/weekly-report", label: "Weekly Report", icon: ClipboardList },
  { href: "/profile", label: "Profile", icon: User },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
    }
  }, [router]);

  // Close mobile menu on navigation
  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  const handleLogout = () => {
    logoutUser();
    router.replace("/login");
  };

  const SidebarContent = () => (
    <>
      {/* Logo */}
      <div className="flex items-center gap-2 px-4 py-4 border-b border-glass-border">
        <span className="text-2xl">🌟</span>
        <div>
          <p className="font-bold text-gray-100 text-sm leading-none">AI Wellness</p>
          <p className="text-xs text-gray-500">Buddy</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => (
          <button
            key={href}
            onClick={() => router.push(href)}
            className={clsx(
              "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors",
              pathname === href
                ? "bg-brand-600/20 text-brand-400 border border-brand-500/30"
                : "text-gray-400 hover:text-gray-100 hover:bg-white/5"
            )}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </nav>

      {/* Calm Mode sidebar controls */}
      <CalmModeSidebar />

      {/* Logout */}
      <div className="px-2 py-4 border-t border-glass-border">
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-gray-400 hover:text-red-400 hover:bg-red-900/10 transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Sign Out
        </button>
      </div>
    </>
  );

  return (
    <div className="flex h-screen bg-gray-950">
      {/* Desktop sidebar — hidden on mobile */}
      <aside className="hidden md:flex flex-col w-56 border-r border-glass-border bg-gray-900/60 backdrop-blur-sm flex-shrink-0">
        <SidebarContent />
      </aside>

      {/* Mobile sidebar overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Mobile sidebar drawer */}
      <aside
        className={clsx(
          "fixed inset-y-0 left-0 z-50 flex flex-col w-64 border-r border-glass-border bg-gray-900 backdrop-blur-sm transform transition-transform duration-200 md:hidden",
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Close button */}
        <button
          onClick={() => setMobileOpen(false)}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-100"
          aria-label="Close menu"
        >
          <X className="w-5 h-5" />
        </button>
        <SidebarContent />
      </aside>

      {/* Main content */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Mobile header with hamburger */}
        <header className="flex items-center gap-3 px-4 py-3 border-b border-glass-border bg-gray-900/60 backdrop-blur-sm md:hidden">
          <button
            onClick={() => setMobileOpen(true)}
            className="text-gray-400 hover:text-gray-100"
            aria-label="Open menu"
          >
            <Menu className="w-5 h-5" />
          </button>
          <span className="text-sm font-semibold text-gray-200">AI Wellness Buddy</span>
        </header>

        <main className="flex-1 overflow-hidden">{children}</main>
      </div>
    </div>
  );
}
