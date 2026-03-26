/**
 * TypingIndicator — animated dots shown while the AI is processing.
 */

export function TypingIndicator() {
  return (
    <div className="flex gap-3 animate-fade-in">
      <div className="w-8 h-8 rounded-full bg-glass border border-glass-border flex items-center justify-center text-sm">
        🤖
      </div>
      <div className="bg-glass border border-glass-border rounded-2xl rounded-tl-sm px-4 py-3 backdrop-blur-sm">
        <div className="flex gap-1 items-center h-4">
          <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]" />
          <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]" />
          <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]" />
        </div>
      </div>
    </div>
  );
}
