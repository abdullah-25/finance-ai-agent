import ChatInput from '../ChatInput';

export default function ChatInputExample() {
  return (
    <div className="max-w-3xl mx-auto border rounded-lg overflow-hidden">
      <ChatInput 
        onSendMessage={(msg) => console.log('Message sent:', msg)} 
      />
    </div>
  );
}
