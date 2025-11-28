export interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatResponse {
  session_id: string;
  response: string;
  current_state: string;
  is_complete: boolean;
}

export interface StartConversationResponse {
  session_id: string;
  message: string;
  current_state: string;
}

export interface ConversationState {
  sessionId: string | null;
  messages: Message[];
  currentState: string;
  isComplete: boolean;
  isLoading: boolean;
}

