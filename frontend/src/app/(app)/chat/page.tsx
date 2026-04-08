/**
 * Chat page — the main ChatGPT-style interface with split-view layout.
 *
 * Features:
 *  - 2-column layout: Chat (70%) | Insights (30%)
 *  - Conversation history loaded from API on mount
 *  - Real-time message exchange with typing indicator
 *  - Emotion badge on every assistant message
 *  - High-risk alert banner + dominant emotion flag
 *  - Voice input (STT) + per-message TTS replay
 *  - Language preference selector (English / Tamil / Bilingual)
 *  - Contextual breathing exercise prompt on anxiety/high-risk
 *  - Mobile-responsive layout (stacked on small screens)
 *  - Robust API response parsing
 */

"use client";

import { useEffect, useRef, useState, useCallback, type KeyboardEvent } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";
import { Globe, AlertCircle, PanelRightOpen, X } from "lucide-react";

import { sendMessage, getChatHistory, getProfile, getErrorMessage, ChatMessage, ChatResponse, EmotionScore } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { InputFooter } from "@/components/chat/InputFooter";
import { AIInsightsCard } from "@/components/chat/AIInsightsCard";
import { EmotionAnalysis } from "@/components/chat/EmotionAnalysis";
import { RiskDashboard } from "@/components/chat/RiskDashboard";
import { FloatingVoiceButton } from "@/components/chat/FloatingVoiceButton";
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
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const [language, setLanguage] = useState<LanguagePreference>("english");
  const [showLangMenu, setShowLangMenu] = useState(false);
  const [showBreathing, setShowBreathing] = useState(false);
  const [breathingPromptVisible, setBreathingPromptVisible] = useState(false);
  const [dominantEmotion, setDominantEmotion] = useState<string | null>(null);
  const [lastRiskScore, setLastRiskScore] = useState(0);
  const [lastHighRisk, setLastHighRisk] = useState(false);
  const [lastEscalation, setLastEscalation] = useState<string | null>(null);
  const [lastConfidence, setLastConfidence] = useState(0);
  const [lastResponseType, setLastResponseType] = useState<"generic" | "personalized" | undefined>(undefined);
  const [lastPersonalizationScore, setLastPersonalizationScore] = useState<number | undefined>(undefined);
  const [lastUsedTriggers, setLastUsedTriggers] = useState<string[]>([]);
  const [showMobileInsights, setShowMobileInsights] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const getRiskScore = useCallback((res: ChatResponse): number => {
    const scores = Array.isArray(res.scores) ? res.scores : [];
    const crisisEntry = scores.find((entry) => String(entry.emotion ?? "") === "crisis");
    const crisisScore = Number(crisisEntry?.score ?? 0);
    if (Number.isFinite(crisisScore) && crisisScore >= 0) {
      return Math.min(1, Math.max(0, crisisScore));
    }
    return res.is_high_risk ? Math.max(0.7, res.confidence) : res.confidence;
  }, []);

  const getNormalizedReply = useCallback((res: ChatResponse): string => {
    const resolved = (
      res.response ??
      res.reply ??
      res.message ??
      res.bot_response ??
      res.response_text ??
      res.text ??
      ""
    ).trim();

    return resolved || "I'm here with you. Please try again.";
  }, []);

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
    setIsLoadingHistory(true);
    setHistoryError(null);
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
      .catch((err) => {
        console.error("Failed to load chat history:", err);
        setHistoryError("Could not load chat history. Starting fresh.");
      })
      .finally(() => {
        setIsLoadingHistory(false);
      });
  }, []);

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
      const botReply = getNormalizedReply(res);

      console.log("[Chat] Response received:", {
        session_id: res.session_id,
        primary_emotion: res.primary_emotion,
        confidence: res.confidence,
        is_high_risk: res.is_high_risk,
        reply_length: botReply.length,
        scores: res.scores,
        response_type: res.response_type,
        personalization_score: res.personalization_score,
      });

      // Guard against empty or missing reply — never render a blank bubble.
      if (!res.reply?.trim()) {
        console.warn("[Chat] Empty reply received from backend:", res);
      }

      if (!sessionId) setSessionId(res.session_id);

      setDominantEmotion(res.primary_emotion);
      setLastConfidence(res.confidence);
      setLastHighRisk(res.is_high_risk);
      setLastEscalation(res.escalation_message);
      setLastRiskScore(getRiskScore(res));
      setLastResponseType(res.response_type);
      setLastPersonalizationScore(res.personalization_score);
      setLastUsedTriggers(Array.isArray(res.used_triggers) ? res.used_triggers : []);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: botReply,
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
  }, [getNormalizedReply, getRiskScore, input, isLoading, sessionId, language]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
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

      {/* Header bar */}
      <div className="relative z-10 flex items-center justify-between px-4 py-2 border-b border-glass-border bg-gray-900/60 backdrop-blur-sm">
        <div className="flex items-center gap-2">
          {isLoading && (
            <span className="inline-flex items-center gap-2 px-2 py-1 rounded-full border border-glass-border bg-white/5 text-xs text-gray-300">
              <span className="w-3 h-3 border-2 border-gray-500 border-t-brand-400 rounded-full animate-spin" />
              Responding...
            </span>
          )}
          {dominantEmotion && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/5 border border-glass-border text-xs text-gray-300">
              <span
                className="w-2 h-2 rounded-full"
                style={{
                  background:
                    dominantEmotion === "crisis"
                      ? "#dc2626"
                      : dominantEmotion === "anxiety" || dominantEmotion === "stress"
                      ? "#f97316"
                      : "#818cf8",
                }}
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
            {t("chat.language.label", language)}: <span className="text-brand-400">{langShortLabel(language)}</span>
          </button>
          {showLangMenu && (
            <div className="absolute right-0 top-full mt-1 w-44 rounded-xl border border-glass-border bg-gray-900 shadow-xl z-20 py-1">
              {LANG_OPTIONS.map((lang) => (
                <button
                  key={lang}
                  type="button"
                  onClick={() => {
                    setLanguage(lang);
                    setShowLangMenu(false);
                  }}
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

      {/* Error banner for history loading */}
      {historyError && (
        <div className="relative z-10 mx-4 mt-3 flex items-center gap-2 rounded-lg border border-amber-500/30 bg-amber-900/20 px-4 py-2 text-sm">
          <AlertCircle className="w-4 h-4 text-amber-300 flex-shrink-0" />
          <span className="text-xs text-amber-200">{historyError}</span>
        </div>
      )}

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

      {/* Main content area - 2 column layout */}
      <div className="relative z-10 flex-1 flex flex-col lg:flex-row gap-0 overflow-hidden">
        {/* Left: Chat window (70% on desktop, full on mobile) */}
        <div className="flex-1 flex flex-col lg:basis-[70%] lg:max-w-[70%] bg-slate-950/65 backdrop-blur-xs border-r border-slate-700/40">
          <ChatWindow
            messages={messages}
            isLoading={isLoading || isLoadingHistory}
            language={language}
          />

          <InputFooter
            value={input}
            onChange={setInput}
            onKeyDown={handleKeyDown}
            onSend={handleSend}
            isLoading={isLoading}
            language={language}
            textareaRef={textareaRef}
          />
        </div>

        {/* Right: Insights panel (30% on desktop, hidden on mobile) */}
        <div className="hidden lg:flex lg:basis-[30%] lg:max-w-[30%] bg-slate-900/75 backdrop-blur-md overflow-hidden">
          <div className="w-full h-full overflow-y-auto px-4 py-4">
            <div className="space-y-4">
              <AIInsightsCard
                isLoading={isLoading || isLoadingHistory}
                responseType={lastResponseType}
                personalizationScore={lastPersonalizationScore}
                usedTriggers={lastUsedTriggers}
                dominantEmotion={dominantEmotion}
              />
              <EmotionAnalysis
                isLoading={isLoading || isLoadingHistory}
                dominantEmotion={dominantEmotion}
                confidenceScore={lastConfidence}
                emotionHistory={[
                  ...messages
                    .filter((m) => m.role === "assistant" && m.emotion)
                    .map((m) => ({
                      emotion: m.emotion || "unknown",
                      confidence: m.confidence || 0,
                    }))
                    .reverse()
                    .slice(0, 5)
                    .reverse(),
                ]}
              />
              <RiskDashboard
                isLoading={isLoading || isLoadingHistory}
                isHighRisk={lastHighRisk}
                escalationMessage={lastEscalation}
                riskScore={lastRiskScore}
                confidenceScore={lastConfidence}
              />
            </div>
          </div>
        </div>
      </div>

      <FloatingVoiceButton
        language={language}
        onTranscript={handleVoiceTranscript}
        disabled={isLoading}
      />

      <button
        type="button"
        onClick={() => setShowMobileInsights(true)}
        className="lg:hidden fixed left-4 bottom-24 z-50 inline-flex items-center gap-2 rounded-xl border border-slate-500/70 bg-slate-900/90 px-3 py-2 text-xs font-medium text-slate-100 shadow-xl"
      >
        <PanelRightOpen className="w-4 h-4" />
        Insights
      </button>

      {showMobileInsights && (
        <div className="lg:hidden fixed inset-0 z-[60]">
          <div
            className="absolute inset-0 bg-black/60"
            onClick={() => setShowMobileInsights(false)}
          />
          <aside className="absolute right-0 top-0 h-full w-[88%] max-w-sm border-l border-slate-500/60 bg-slate-950/95 backdrop-blur-md p-4 overflow-y-auto">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold text-slate-100">Insights</h2>
              <button
                type="button"
                onClick={() => setShowMobileInsights(false)}
                className="rounded-md border border-slate-600/70 p-1.5 text-slate-200"
                aria-label="Close insights"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="space-y-4">
              <AIInsightsCard
                isLoading={isLoading || isLoadingHistory}
                responseType={lastResponseType}
                personalizationScore={lastPersonalizationScore}
                usedTriggers={lastUsedTriggers}
                dominantEmotion={dominantEmotion}
              />
              <EmotionAnalysis
                isLoading={isLoading || isLoadingHistory}
                dominantEmotion={dominantEmotion}
                confidenceScore={lastConfidence}
                emotionHistory={[
                  ...messages
                    .filter((m) => m.role === "assistant" && m.emotion)
                    .map((m) => ({
                      emotion: m.emotion || "unknown",
                      confidence: m.confidence || 0,
                    }))
                    .reverse()
                    .slice(0, 5)
                    .reverse(),
                ]}
              />
              <RiskDashboard
                isLoading={isLoading || isLoadingHistory}
                isHighRisk={lastHighRisk}
                escalationMessage={lastEscalation}
                riskScore={lastRiskScore}
                confidenceScore={lastConfidence}
              />
            </div>
          </aside>
        </div>
      )}
    </div>
  );
}

