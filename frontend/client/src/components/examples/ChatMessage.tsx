import ChatMessage from '../ChatMessage';

export default function ChatMessageExample() {
  return (
    <div className="space-y-4 p-4 max-w-3xl mx-auto">
      <ChatMessage 
        role="user" 
        content="Which stocks should I buy today?" 
        timestamp="2:30 PM"
      />
      <ChatMessage 
        role="assistant" 
        content="Based on current market conditions, I recommend considering tech stocks like AAPL and MSFT. Both show strong fundamentals and positive momentum." 
        timestamp="2:30 PM"
      />
    </div>
  );
}
