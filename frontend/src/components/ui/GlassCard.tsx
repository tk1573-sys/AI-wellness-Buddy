/**
 * Reusable glassmorphism card component.
 */

import { clsx } from "clsx";
import { ReactNode } from "react";

interface GlassCardProps {
  children: ReactNode;
  className?: string;
}

export function GlassCard({ children, className }: GlassCardProps) {
  return (
    <div
      className={clsx(
        "rounded-2xl border border-glass-border bg-glass backdrop-blur-sm",
        className
      )}
    >
      {children}
    </div>
  );
}
