// import {
//   PromptInput,
//   PromptInputButton,
//   PromptInputModelSelect,
//   PromptInputModelSelectContent,
//   PromptInputModelSelectItem,
//   PromptInputModelSelectTrigger,
//   PromptInputModelSelectValue,
//   PromptInputSubmit,
//   PromptInputTextarea,
//   PromptInputToolbar,
//   PromptInputTools,
// } from '@/components/ui/shadcn-io/ai/prompt-input';
// import { MicIcon, PaperclipIcon } from 'lucide-react';
// import React, { useCallback, useState, type FormEventHandler } from 'react';
// import { nanoid } from 'nanoid';

// interface Model {
//   id: string;
//   name: string;
// }

// interface ChatInputProps {
//   inputValue: string;
//   onInputChange: (value: string) => void;
//   selectedModel: string;
//   onModelChange: (model: string) => void;
//   onSubmit: () => void;
//   isTyping: boolean;
//   models: Model[];
//   placeholder?: string;
// }

// type ChatMessage = {
//   id: string;
//   content: string;
//   role: 'user' | 'assistant';
//   timestamp: Date;
//   reasoning?: string;
//   sources?: Array<{ title: string; url: string }>;
//   isStreaming?: boolean;
// };

// export const ChatInput: React.FC<ChatInputProps> = ({
//   inputValue,
//   onInputChange,
//   selectedModel,
//   onModelChange,
//   onSubmit,
//   isTyping,
//   models,
//   placeholder = "Ask me anything about development, coding, or technology..."
// }) => {
//    const [messages, setMessages] = useState<ChatMessage[]>([
//         {
//         id: nanoid(),
//         content: "Hello! I'm your AI assistant. I can help you with coding questions, explain concepts, and provide guidance on web development topics. What would you like to know?",
//         role: 'assistant',
//         timestamp: new Date(),
//         sources: [
//             { title: "Getting Started Guide", url: "#" },
//             { title: "API Documentation", url: "#" }
//         ]
//         }
//     ]);
//    const [inputValue, setInputValue] = useState('');
//    const handleSubmit: FormEventHandler<HTMLFormElement> = useCallback((event) => {
//     event.preventDefault();
    
//     if (!inputValue.trim() || isTyping) return;
//     // Add user message
//     const userMessage: ChatMessage = {
//       id: nanoid(),
//       content: inputValue.trim(),
//       role: 'user',
//       timestamp: new Date(),
//     };
//     setMessages((prev: any) => [...prev, userMessage]);
//     setInputValue('');
//     setIsTyping(true);
//     // Simulate AI response with delay
//     setTimeout(() => {
//       const responseData = sampleResponses[Math.floor(Math.random() * sampleResponses.length)];
//       const assistantMessageId = nanoid();
      
//       const assistantMessage: ChatMessage = {
//         id: assistantMessageId,
//         content: '',
//         role: 'assistant',
//         timestamp: new Date(),
//         isStreaming: true,
//       };
//       setMessages(prev => [...prev, assistantMessage]);
//       setStreamingMessageId(assistantMessageId);
      
//       // Start typing simulation
//       simulateTyping(assistantMessageId, responseData.content, responseData.reasoning, responseData.sources);
//     }, 800);
//   }, [inputValue, isTyping, simulateTyping]);

//   return (
//     <div className="border-t p-4">
//       <PromptInput onSubmit={handleSubmit}>
//         <PromptInputTextarea
//           value={inputValue}
//           onChange={(e) => onInputChange(e.target.value)}
//           placeholder={placeholder}
//           disabled={isTyping}
//         />
//         <PromptInputToolbar>
//           <PromptInputTools>
//             <PromptInputButton disabled={isTyping}>
//               <PaperclipIcon size={16} />
//             </PromptInputButton>
//             <PromptInputButton disabled={isTyping}>
//               <MicIcon size={16} />
//               <span>Voice</span>
//             </PromptInputButton>
//             <PromptInputModelSelect 
//               value={selectedModel} 
//               onValueChange={onModelChange}
//               disabled={isTyping}
//             >
//               <PromptInputModelSelectTrigger>
//                 <PromptInputModelSelectValue />
//               </PromptInputModelSelectTrigger>
//               <PromptInputModelSelectContent>
//                 {models.map((model) => (
//                   <PromptInputModelSelectItem key={model.id} value={model.id}>
//                     {model.name}
//                   </PromptInputModelSelectItem>
//                 ))}
//               </PromptInputModelSelectContent>
//             </PromptInputModelSelect>
//           </PromptInputTools>
//           <PromptInputSubmit 
//             disabled={!inputValue.trim() || isTyping}
//             status={isTyping ? 'streaming' : 'ready'}
//           />
//         </PromptInputToolbar>
//       </PromptInput>
//     </div>
//   );
// };