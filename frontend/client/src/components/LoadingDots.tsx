export default function LoadingDots() {
  return (
    <div className="flex items-center space-x-2 px-4 py-3 bg-muted rounded-2xl max-w-[80%]" data-testid="loading-indicator">
      <div className="flex space-x-1">
        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse-dot" style={{ animationDelay: "0ms" }} />
        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse-dot" style={{ animationDelay: "200ms" }} />
        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse-dot" style={{ animationDelay: "400ms" }} />
      </div>
    </div>
  );
}
