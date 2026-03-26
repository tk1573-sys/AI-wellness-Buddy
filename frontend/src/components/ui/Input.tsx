/**
 * Styled text input for dark glassmorphism UI.
 */

import { clsx } from "clsx";
import { InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function Input({ label, error, className, id, ...rest }: InputProps) {
  return (
    <div className="w-full space-y-1">
      {label && (
        <label htmlFor={id} className="block text-sm font-medium text-gray-300">
          {label}
        </label>
      )}
      <input
        id={id}
        {...rest}
        className={clsx(
          "w-full rounded-xl border bg-white/5 px-4 py-2.5 text-sm text-gray-100 placeholder:text-gray-500 transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500",
          error
            ? "border-red-500/60 focus:ring-red-500"
            : "border-glass-border focus:border-brand-500",
          className
        )}
      />
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}
