/**
 * Signup page — register a new account.
 */

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import toast from "react-hot-toast";

import { signupUser } from "@/lib/auth";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { GlassCard } from "@/components/ui/GlassCard";

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{
    email?: string; username?: string; password?: string;
  }>({});

  const validate = () => {
    const e: typeof errors = {};
    if (!email.includes("@")) e.email = "Enter a valid email.";
    if (username.length < 3) e.username = "Username must be at least 3 characters.";
    const pwdErrors: string[] = [];
    if (password.length < 8) pwdErrors.push("at least 8 characters");
    if (!/[A-Z]/.test(password)) pwdErrors.push("one uppercase letter");
    if (!/\d/.test(password)) pwdErrors.push("one digit");
    if (pwdErrors.length > 0) {
      e.password = `Password must contain: ${pwdErrors.join(", ")}.`;
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (evt: React.FormEvent) => {
    evt.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      await signupUser(email, username, password);
      toast.success("Account created! Welcome 🎉");
      router.push("/onboarding");
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Signup failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-96 h-96 rounded-full bg-purple-600/20 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 rounded-full bg-brand-600/20 blur-3xl" />
      </div>

      <GlassCard className="w-full max-w-md p-8 space-y-6 animate-fade-in relative z-10">
        <div className="text-center space-y-1">
          <h1 className="text-3xl font-bold gradient-text">Create Account</h1>
          <p className="text-gray-400 text-sm">Start your wellness journey today</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            id="email"
            label="Email"
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            error={errors.email}
            autoComplete="email"
          />
          <Input
            id="username"
            label="Username"
            type="text"
            placeholder="yourname"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            error={errors.username}
            autoComplete="username"
          />
          <Input
            id="password"
            label="Password"
            type="password"
            placeholder="Min. 8 chars, 1 uppercase, 1 digit"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            error={errors.password}
            autoComplete="new-password"
          />
          <Button type="submit" loading={loading} className="w-full mt-2">
            Create Account
          </Button>
        </form>

        <p className="text-center text-sm text-gray-400">
          Already have an account?{" "}
          <Link href="/login" className="text-brand-400 hover:underline">
            Sign in
          </Link>
        </p>
      </GlassCard>
    </main>
  );
}
