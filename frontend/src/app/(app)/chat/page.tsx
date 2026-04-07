/**
 * Chat page — split-pane healthcare interface.
 *
 * Features:
 *  - 70/30 desktop split: chat window (left) + analysis sidebar (right)
 *  - Conversation history loaded from API on mount
 *  - Real-time message exchange with typing indicator
 *  - Emotion badge on every assistant message
 *  - High-risk alert banner + dominant emotion flag
 *  - Voice input (STT) + per-message TTS replay
 *  - Language preference selector (English / Tamil / Bilingual)
 *  - Contextual breathing exercise prompt on anxiety/high-risk
 *  - Guardian-alert / onboarding compatible (uses latest API types)
 *  - Response normalization: reply | response | message | bot_response | response_text
 *  - Dark healthcare theme
 */

"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";
import { Globe } from "lucide-react";

import { sendMessage, getChatHistory, getProfile, getErrorMessage, ChatMessage, ChatResponse, EmotionScore } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import { ChatBubble } from "@/components/chat/ChatBubble";
import { TypingIndicator } from "@/components/chat/TypingIndicator";
import { TtsPlayer } from "@/components/chat/TtsPlayer";
import { InsightsPanel } from "@/components/chat/InsightsPanel";
import { RiskDashboard } from "@/components/chat/RiskDashboard";
import { EmotionAnalysis } from "@/components/chat/EmotionAnalysis";
import { InputFooter } from "@/components/chat/InputFooter";
import { BreathingExercise } from "@/components/wellness/BreathingExercise";
import { t, langLabel, langShortLabel, type LanguagePreference } from "@/lib/i18n";

interface Message {
  role: "user" | "assistant";
  content: string;
  emotion?: string | null;
  confidence?: number;
  isHighRisk?: boolean;
  escalationMessage?: string | null;
  scores?: EmotionScore[];
  responseType?: "generic" | "personalized";
  personalizationScore?: number;
}

const ANXIETY_EMOTIONS = new Set(["anxiety", "fear", "stress", "crisis"]);

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const [language, setLanguage] = useState<LanguagePreference>("english");
  const [showLangMenu, setShowLangMenu] = useState(false);
  const [showBreathing, setShowBreathing] = useState(false);
  const [breathingPromptVisible, setBreathingPromptVisible] = useState(false);
  const [dominantEmotion, setDominantEmotion] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
    }
  }, [router]);

  // Load language preference from profile on mount
  useEffect(() => {
    getProfile()
      .then((p) => {
        if (p.language_preference) {
          setLanguage(p.language_preference as LanguagePreference);
        }
      })
      .catch(() => {/* ignore */});
  }, []);

  // Load existing chat history on mount
  useEffect(() => {
    getChatHistory()
      .then((history: ChatMessage[]) => {
        if (history.length > 0) {
          setMessages(
            history.map((m) => ({
              role: m.role as "user" | "assistant",
              content: m.content,
              emotion: m.emotion,
            }))
          );
        }
      })
      .catch(() => {
        // First-time user — no history yet, that's fine
      });
  }, []);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = useCallback(async () => {
    const text = input.trim();
    if (!text || isLoading) return;

    console.log("[Chat] Sending message:", { text, sessionId, language });

    setInput("");
    setBreathingPromptVisible(false);
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setIsLoading(true);

    try {
      const res: ChatResponse = await sendMessage(text, sessionId, language);
      console.log("[Chat] Response received:", {
        session_id: res.session_id,
        primary_emotion: res.primary_emotion,
        confidence: res.confidence,
        is_high_risk: res.is_high_risk,
        reply_length: res.reply?.length ?? 0,
        scores: res.scores,
        response_type: res.response_type,
        personalization_score: res.personalization_score,
      });

      // Guard against empty or missing reply — never render a blank bubble.
      const replyText = res.reply?.trim()
        || "I'm here with you. Please try again in a moment.";

      if (!res.reply?.trim()) {
        console.warn("[Chat] Empty reply received from backend:", res);
      }

      if (!sessionId) setSessionId(res.session_id);

      setDominantEmotion(res.primary_emotion);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: replyText,
          emotion: res.primary_emotion,
          confidence: res.confidence,
          isHighRisk: res.is_high_risk,
          escalationMessage: res.escalation_message,
          scores: res.scores,
          responseType: res.response_type,
          personalizationScore: res.personalization_score,
        },
      ]);

      // Show breathing prompt on anxiety/high-risk
      if (res.is_high_risk || ANXIETY_EMOTIONS.has(res.primary_emotion)) {
        setBreathingPromptVisible(true);
      }

      if (res.is_high_risk) {
        toast.error("High-risk content detected. Please seek support.", {
          duration: 8000,
          icon: "🆘",
        });
      }
    } catch (err: unknown) {
      const msg = getErrorMessage(err);
      console.error("[Chat] Send failed:", err, "→", msg);
      toast.error(msg);
      // Restore the user's text so they can retry; remove the optimistic message.
      // Only restore if the textarea is still empty (user hasn't started a new message).
      setInput((prev) => (prev === "" ? text : prev));
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
      textareaRef.current?.focus();
    }
  }, [input, isLoading, sessionId, language]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleVoiceTranscript = (text: string) => {
    setInput((prev) => prev + (prev ? " " : "") + text);
    textareaRef.current?.focus();
  };

  const LANG_OPTIONS: LanguagePreference[] = ["english", "tamil", "bilingual"];

  return (
    <div className="flex flex-col h-full bg-gray-950">
      {/* Background blobs */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute top-0 left-1/4 w-80 h-80 rounded-full bg-brand-600/10 blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-80 h-80 rounded-full bg-purple-600/10 blur-3xl" />
      </div>

      {/* Header bar — dominant emotion flag + language badge */}
      <div className="relative z-10 flex items-center justify-between px-4 py-2 border-b border-glass-border bg-gray-900/60 backdrop-blur-sm">
        <div className="flex items-center gap-2">
          {dominantEmotion && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/5 border border-glass-border text-xs text-gray-300">
              <span
                className="w-2 h-2 rounded-full"
                style={{ background: dominantEmotion === "crisis" ? "#dc2626" : "#818cf8" }}
              />
              {dominantEmotion.charAt(0).toUpperCase() + dominantEmotion.slice(1)}
            </span>
          )}
        </div>

        {/* Language selector */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setShowLangMenu((s) => !s)}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl border border-glass-border text-xs text-gray-400 hover:text-gray-100 hover:bg-white/5 transition-colors"
          >
            <Globe className="w-3 h-3" />
            {t("chat.language.label", language)}:{" "}
            <span className="text-brand-400">{langShortLabel(language)}</span>
          </button>
          {showLangMenu && (
            <div className="absolute right-0 top-full mt-1 w-44 rounded-xl border border-glass-border bg-gray-900 shadow-xl z-20 py-1">
              {LANG_OPTIONS.map((lang) => (
                <button
                  key={lang}
                  type="button"
                  onClick={() => { setLanguage(lang); setShowLangMenu(false); }}
                  className={`w-full text-left px-3 py-2 text-xs transition-colors ${
                    language === lang
                      ? "text-brand-400 bg-brand-600/10"
                      : "text-gray-400 hover:text-gray-100 hover:bg-white/5"
                  }`}
                >
                  {langLabel(lang)}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Breathing exercise prompt */}
      {breathingPromptVisible && !showBreathing && (
        <div className="relative z-10 mx-4 mt-3 flex items-center gap-3 rounded-xl border border-amber-500/30 bg-amber-900/20 px-4 py-3 text-sm">
          <span>🌬️</span>
          <span className="flex-1 text-amber-200 text-xs">
            {t("chat.breathing.prompt", language)}
          </span>
          <button
            type="button"
            onClick={() => setShowBreathing(true)}
            className="flex-shrink-0 text-xs px-3 py-1.5 rounded-lg bg-amber-600/30 border border-amber-500/50 text-amber-300 hover:bg-amber-600/40 transition-colors"
          >
            {t("chat.breathing.start", language)}
          </button>
          <button
            type="button"
            onClick={() => setBreathingPromptVisible(false)}
            className="flex-shrink-0 text-gray-500 hover:text-gray-300 text-xs"
          >
            ✕
          </button>
        </div>
      )}

      {/* Breathing exercise overlay */}
      {showBreathing && (
        <div className="relative z-10 mx-4 mt-3 rounded-xl border border-brand-500/30 bg-gray-900/80 backdrop-blur-sm p-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs font-semibold text-brand-300">🌬️ Breathing Exercise</span>
            <button
              type="button"
              onClick={() => setShowBreathing(false)}
              className="text-xs text-gray-500 hover:text-gray-300"
            >
              {t("chat.breathing.stop", language)}
            </button>
          </div>
          <BreathingExercise language={language} />
        </div>
      )}

      {/* ------------------------------------------------------------------ */}
      {/* 70 / 30 split — chat window (left) + analysis sidebar (right)       */}
      {/* The sidebar is hidden on mobile and shown as a fixed column on lg+. */}
      {/* ------------------------------------------------------------------ */}
      <div className="relative z-10 flex flex-1 overflow-hidden">

        {/* ── Left panel: chat messages (70%) ── */}
        <div className="flex flex-col flex-[7] min-w-0 overflow-hidden">
          <main className="flex-1 overflow-y-auto px-4 py-6 space-y-5">
            {messages.length === 0 && !isLoading && (
              <div className="flex flex-col items-center justify-center h-full space-y-3 text-center animate-fade-in">
                <span className="text-5xl">💬</span>
                <h2 className="text-xl font-semibold text-gray-200">
                  {t("chat.welcome.title", language)}
                </h2>
                <p className="text-gray-500 text-sm max-w-xs">
                  {t("chat.welcome.subtitle", language)}
                </p>
              </div>
            )}

            {messages.map((msg, i) => (
              <div key={i} className="flex flex-col">
                <ChatBubble
                  role={msg.role}
                  content={msg.content}
                  emotion={msg.emotion}
                  confidence={msg.confidence}
                  isHighRisk={msg.isHighRisk}
                  escalationMessage={msg.escalationMessage}
                />
                {/* Per-message insights + TTS replay (assistant only) */}
                {msg.role === "assistant" && (
                  <>
                    <InsightsPanel
                      scores={msg.scores ?? []}
                      responseType={msg.responseType}
                      personalizationScore={msg.personalizationScore}
                    />
                    <div className="flex justify-start pl-4 mt-0.5">
                      <TtsPlayer text={msg.content} language={language} messageKey={i} />
                    </div>
                  </>
                )}
              </div>
            ))}

            {isLoading && <TypingIndicator />}

            <div ref={bottomRef} />
          </main>

          {/* Input footer (part of the left column) */}
          <InputFooter
            language={language}
            input={input}
            isLoading={isLoading}
            textareaRef={textareaRef}
            onInputChange={setInput}
            onKeyDown={handleKeyDown}
            onSend={handleSend}
            onVoiceTranscript={handleVoiceTranscript}
          />
        </div>

        {/* ── Right panel: analysis sidebar (30%) — desktop only ── */}
        <aside className="hidden lg:flex flex-col flex-[3] min-w-0 overflow-y-auto border-l border-glass-border bg-gray-900/40 backdrop-blur-sm px-4 py-5 space-y-4">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-widest">
            Session Analysis
          </p>
          <RiskDashboard messages={messages} />
          <EmotionAnalysis messages={messages} />
        </aside>
      </div>
    </div>
  );
}
