'use client';
import {
  Conversation,
  ConversationContent,
  ConversationScrollButton,
} from '@/components/ui/shadcn-io/ai/conversation';
import { Loader } from '@/components/ui/shadcn-io/ai/loader';
import { Message, MessageAvatar, MessageContent } from '@/components/ui/shadcn-io/ai/message';
import {
  PromptInput,
  PromptInputSubmit,
  PromptInputTextarea,
  PromptInputToolbar,
} from '@/components/ui/shadcn-io/ai/prompt-input';
import {
  Reasoning,
  ReasoningContent,
  ReasoningTrigger,
} from '@/components/ui/shadcn-io/ai/reasoning';
import { Source, Sources, SourcesContent, SourcesTrigger } from '@/components/ui/shadcn-io/ai/source';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { RotateCcwIcon } from 'lucide-react';
import { nanoid } from 'nanoid';
import { type FormEventHandler, useCallback, useEffect, useRef, useState } from 'react';

// user provider 
import React from "react";
import UseApi from "../hooks/UseApi";
import type { UserSchema } from "../context/UserProvider";
import { useNavigate, useParams } from "react-router-dom";
// import useUser from "../hooks/UseUser";

import type { FhirQueryResponse } from '@/schemas/fhirResponse';
import Config from '@/config';
import { FhirQueryVisualizer } from './Charts';
import { useGetUserDetailsQuery } from '@/services/user';
import { useSelector } from 'react-redux';
import SpinnerLineWave from './Spinner';
import type { RootState } from '@/store';


const SUGGESTIONS: string[] = [
  'Show me all diabetic patients over 50',
  'List hypertensive patients under 40',
  'Patients with asthma by city',
  'Show female patients over 60 with diabetes',
  'All pediatric patients with immunizations',
];

function useDebounce<T extends (...args: any[]) => void>(
  fn: T,
  delay: number
): T {
  // Use a ref to store the timeout ID, ensuring it persists across renders
  const timeoutRef = useRef<number | undefined>(undefined);

  // The function returned by useCallback is the debounced function
  return useCallback((...args: Parameters<T>) => {
    // Clear the previous timeout, if it exists
    if (timeoutRef.current) {
      window.clearTimeout(timeoutRef.current);
    }

    // Set a new timeout
    // Note: window.setTimeout returns a number (or Node.js Timer object, hence the number type)
    const newTimeoutId = window.setTimeout(() => {
      fn(...args);
    }, delay);
    
    // Store the new timeout ID
    timeoutRef.current = newTimeoutId;
  }, [fn, delay]) as T; 
  // We assert the return type back to T to maintain the function signature 
  // and ensure TypeScript knows the debounced function accepts the same arguments.
}

type ChatMessage = {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  reasoning?: string;
  sources?: Array<{ title: string; url: string }>;
  isStreaming?: boolean;
  fhirResponse?: FhirQueryResponse;
};


const FhirBot = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: nanoid(),
      content: "Hello! I'm your AI-powered healthcare data querying tool that interfaces with FHIR-compliant systems. What would you like to know?",
      role: 'assistant',
      timestamp: new Date(),
      sources: [
        { title: "FHIR API", url: "#" },
      ]
    }
  ]);
  const {id} = useParams();

  // query input and suggestions 
  const [inputValue, setInputValue] = useState<string>('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const navigate = useNavigate();


  // user 
  // Get the user state from Redux
  const token = useSelector((state: RootState) => state.user.token);
  // automatically authenticate user if token is found
  const { data: user, isLoading: isUserLoading } = useGetUserDetailsQuery(token, {
    pollingInterval: 9000,
    // Now skips if the token is null/undefined (e.g., user is logged out)
    skip: !token, 
  });
 
  const [isTyping, setIsTyping] = useState(false);
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null);
  
  // result setting 
  const [results, setResults] = useState<FhirQueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const simulateTyping = useCallback((messageId: string, content: string, reasoning?: string, sources?: Array<{ title: string; url: string }>) => {
    let currentIndex = 0;
    const typeInterval = setInterval(() => {
      setMessages(prev => prev.map(msg => {
        if (msg.id === messageId) {
          const currentContent = content.slice(0, currentIndex);
          return {
            ...msg,
            content: currentContent,
            isStreaming: currentIndex < content.length,
            reasoning: currentIndex >= content.length ? reasoning : undefined,
            sources: currentIndex >= content.length ? sources : undefined,
          };
        }
        return msg;
      }));
      currentIndex += Math.random() > 0.1 ? 1 : 0; // Simulate variable typing speed
      
      if (currentIndex >= content.length) {
        clearInterval(typeInterval);
        setIsTyping(false);
        setStreamingMessageId(null);
      }
    }, 50);
    return () => clearInterval(typeInterval);
  }, []);

  // -----------------------------
  // Execute query (POST) and set results
  // -----------------------------
  
  const handleSubmit: FormEventHandler<HTMLFormElement> = useCallback(
    async (event) => {
      event.preventDefault();

      if (!inputValue.trim() || isTyping) return;

      // Add user message
      const userMessage: ChatMessage = {
        id: nanoid(),
        content: inputValue.trim(),
        role: 'user',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setInputValue('');
      setIsTyping(true);

      try {
        // Send POST request to your backend
        const resp = await fetch(`${Config.baseURL}/query`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: inputValue.trim() }),
        });

        if (!resp.ok) throw new Error(`Server returned ${resp.status}`);

        // Parse FhirQueryResponse
        const data: FhirQueryResponse = await resp.json();
        console.log(data)

        // Build assistant message based on the structured response
        const assistantMessageId = nanoid();
        const assistantMessage: ChatMessage = {
          id: assistantMessageId,
          role: 'assistant',
          content: '',
          fhirResponse: data,
          timestamp: new Date(),
        };

        // Optional: you could render structured components (charts/tables) from `data.processed_results`
        setMessages((prev) => [...prev, assistantMessage]);
      } catch (err) {
        console.error('FHIR Query Error:', err);

        const errorMessage: ChatMessage = {
          id: nanoid(),
          role: 'assistant',
          content: '⚠️ Something went wrong while processing your query.',
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsTyping(false);
      }
    },
    [inputValue, isTyping]
  );

  const handleReset = useCallback(() => {
    setMessages([
      {
        id: nanoid(),
        content: "Hello! I'm your AI-powered healthcare data querying tool that interfaces with FHIR-compliant systems. What would you like to know?",
        role: 'assistant',
        timestamp: new Date(),
        sources: [
          { title: "FHIR API", url: "#" },
        ]
      }
    ]);
    setInputValue('');
    setIsTyping(false);
    setStreamingMessageId(null);
  }, []);

  // Suggestion fetcher (debounced)
  const debouncedFilter = useDebounce((value) => {
    if (!value.trim()) {
      setSuggestions([]);
    return;
  }
  const filtered = SUGGESTIONS.filter((s) => s.toLowerCase().includes(value.toLowerCase()));
    setSuggestions(filtered);
  }, 300);


  const handleChange = (e : React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const value = e.target.value;
    setInputValue(value);
    debouncedFilter(value);
  };

  
  // function onSelectSuggestion(s: string) {
  //   setQuery(s);
  //   setShowSuggestions(false);
  //   executeQuery(s);
  // }

  const handleLogout = useCallback(() => {
    // Clear stored tokens or session data
    localStorage.removeItem('authToken');
    sessionStorage.clear();

    // Optionally show a message or toast
    alert('You have been logged out.');

    // Redirect to login page
    navigate('/login');
  }, [navigate]);

  return (
    <div className="flex h-full w-full flex-col overflow-hidden rounded-xl border bg-[url('/gradient-other.png')] bg-cover backdrop-blur-sm shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between border-b bg-muted/50 px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="size-2 rounded-full bg-green-500" />
            <span className="font-medium text-sm">FHIR Assistant</span>
             
          </div>
          <div className="h-4 w-px bg-border" />
          {/* { user && (
          <> */}
          <span className='text-black'> Welcome {user?.username}</span>
          {/* </>
          )} */}
        </div>

        
        { user?.email && (
          <>
            <div className="col-span-6 sm:flex sm:items-center sm:gap-4">
              <a 
                className="inline-block shrink-0 rounded-md border border-green-600 bg-green-600 px-10 py-3 text-sm font-medium text-white transition hover:bg-transparent hover:text-black focus:outline-none focus:ring active:text-green-500"
                href="#logout"
                onClick={(e) => {
                  e.preventDefault();
                  handleLogout();
                }}
              >
              <button
                className=""
              
              >
              </button>
              Logout!</a>

          </div>
          </>
        )}

        { !user?.email && (
          <>
            <div className="col-span-6 sm:flex sm:items-center sm:gap-4">
              <a href="/login" className="inline-block shrink-0 rounded-md border border-blue-600 bg-blue-600 px-10 py-3 text-sm font-medium text-white transition hover:bg-transparent hover:text-blue-600 focus:outline-none focus:ring active:text-blue-500">
              <button
                className=""
                type="submit" aria-disabled={loading}
              >
              </button>
              Sign in!</a>

            <p className="mt-4 text-sm text-gray-500 sm:mt-0">
              Don't have an account?
              <a href="/register" className="text-gray-700 underline"> Sign up!</a>.
            </p>
          </div>
          </>
        )}

        <Button 
          variant="ghost" 
          size="sm"
          onClick={handleReset}
          className="h-8 px-2"
        >
          <RotateCcwIcon className="size-4" />
          <span className="ml-1">Reset</span>
        </Button>
      </div>
      {/* Conversation Area */}
      <Conversation className="flex-1">
        <ConversationContent className="space-y-4">
          {messages.map((msg) => (
            <div key={msg.id} className="space-y-3">

              <Message from={msg.role}>
                <MessageContent>
                  {msg.isStreaming && msg.content === '' ? (
                    <div className="flex items-center gap-2">
                      <Loader size={14} />
                      <span className="text-muted-foreground text-sm">Thinking...</span>
                    </div>
                  ) : (
                    ''
                  )}
                
                  <div key={msg.id} className={msg.role === 'user' ? 'text-right' : 'text-left'}>
                    {msg.fhirResponse ? (
                      <FhirQueryVisualizer data={msg.fhirResponse} />
                    ) : (
                      <p className="p-2">{msg.content}</p>
                    )}
                  </div>
                </MessageContent>
                <MessageAvatar 
                    src={msg.role === 'user' ? 'https://github.com/dovazencot.png' : 'https://github.com/vercel.png'} 
                    name={msg.role === 'user' ? 'User' : 'AI'} 
                  />
                
              </Message>
              {/* Reasoning */}
              {msg.reasoning && (
                <div className="ml-10">
                  <Reasoning isStreaming={msg.isStreaming} defaultOpen={false}>
                    <ReasoningTrigger />
                    <ReasoningContent>{msg.reasoning}</ReasoningContent>
                  </Reasoning>
                </div>
              )}
              {/* Sources */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="ml-10">
                  <Sources>
                    <SourcesTrigger count={msg.sources.length} />
                    <SourcesContent>
                      {msg.sources.map((source, index) => (
                        <Source key={index} href={source.url} title={source.title} />
                      ))}
                    </SourcesContent>
                  </Sources>
                </div>
              )}
            </div>
          ))}
          <ConversationScrollButton />
        </ ConversationContent>
      </Conversation>
      {/* Suggestions dropdown */}
      {suggestions.length > 0 && (
        <div className="relative z-10 mx-4 -my-2 bg-white shadow rounded-md w-fit border border-gray-200">
          {suggestions.map((s) => (
            <div
              key={s}
              className="p-2 text-xs hover:bg-gray-100 cursor-pointer"
              onClick={() => {
                setInputValue(s);
                setSuggestions([]);
              }}
              >
              {s}
            </div>
          ))}
        </div>
      )}

      {/* Input Area */}
      <div className="border-t p-4">
        <PromptInput onSubmit={handleSubmit}>
          <PromptInputTextarea
            value={inputValue}
            onChange={handleChange}
            placeholder="Ask me anything about e.g., “Show me all diabetic patients over 50"
            disabled={isTyping}
          />
          <PromptInputToolbar className='justify-end'>
            
            <PromptInputSubmit 
              disabled={!inputValue.trim() || isTyping}
              status={isTyping ? 'streaming' : 'ready'}
            />
          </PromptInputToolbar>
        
        </PromptInput>
      </div>
    </div>
  );
};

export default FhirBot;