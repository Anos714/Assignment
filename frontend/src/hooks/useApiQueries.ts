import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../api";
import type { AuthCredentials, SignupPayload } from "../api";
import { useAppStore } from "../store/useAppStore";

export const queryKeys = {
  me: ["me"] as const,
  stats: ["stats"] as const,
  documents: ["documents"] as const,
  chats: ["chats"] as const,
  chat: (chatId: string | null) => ["chat", chatId] as const,
  ragHealth: ["rag-health"] as const,
};

export function useCurrentUser() {
  const accessToken = useAppStore((state) => state.accessToken);
  return useQuery({
    queryKey: queryKeys.me,
    queryFn: api.me,
    enabled: Boolean(accessToken),
    retry: false,
  });
}

export function useDashboardStats() {
  const accessToken = useAppStore((state) => state.accessToken);
  return useQuery({
    queryKey: queryKeys.stats,
    queryFn: api.getStats,
    enabled: Boolean(accessToken),
  });
}

export function useDocuments() {
  const accessToken = useAppStore((state) => state.accessToken);
  return useQuery({
    queryKey: queryKeys.documents,
    queryFn: api.listDocuments,
    enabled: Boolean(accessToken),
    refetchInterval: (query) => {
      const documents = query.state.data?.results ?? [];
      return documents.some((document) => document.status === "queued" || document.status === "processing")
        ? 4000
        : false;
    },
  });
}

export function useChats() {
  const accessToken = useAppStore((state) => state.accessToken);
  return useQuery({
    queryKey: queryKeys.chats,
    queryFn: api.listChats,
    enabled: Boolean(accessToken),
  });
}

export function useChat(chatId: string | null) {
  const accessToken = useAppStore((state) => state.accessToken);
  return useQuery({
    queryKey: queryKeys.chat(chatId),
    queryFn: () => api.getChat(chatId!),
    enabled: Boolean(accessToken && chatId),
  });
}

export function useRagHealth() {
  return useQuery({
    queryKey: queryKeys.ragHealth,
    queryFn: api.ragHealth,
    retry: false,
    refetchInterval: 30000,
  });
}

export function useLoginMutation() {
  const queryClient = useQueryClient();
  const setTokens = useAppStore((state) => state.setTokens);
  return useMutation({
    mutationFn: (payload: AuthCredentials) => api.login(payload),
    onSuccess: (tokens) => {
      setTokens(tokens);
      void queryClient.invalidateQueries();
    },
  });
}

export function useSignupMutation() {
  return useMutation({
    mutationFn: (payload: SignupPayload) => api.signup(payload),
  });
}

export function useCreateChatMutation() {
  const queryClient = useQueryClient();
  const setActiveChatId = useAppStore((state) => state.setActiveChatId);
  return useMutation({
    mutationFn: (title: string) => api.createChat(title),
    onSuccess: (chat) => {
      setActiveChatId(chat.id);
      void queryClient.invalidateQueries({ queryKey: queryKeys.chats });
      void queryClient.invalidateQueries({ queryKey: queryKeys.stats });
    },
  });
}

export function useAskQuestionMutation(chatId: string | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { question: string; documentIds: string[] }) => {
      if (!chatId) {
        throw new Error("Create or select a chat before asking a question.");
      }
      return api.askQuestion(chatId, payload.question, payload.documentIds);
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.chat(chatId) });
      void queryClient.invalidateQueries({ queryKey: queryKeys.chats });
      void queryClient.invalidateQueries({ queryKey: queryKeys.stats });
    },
  });
}

export function useUploadDocumentMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { file: File; onProgress?: (progress: number) => void }) =>
      api.uploadDocument(payload.file, payload.onProgress),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.documents });
      void queryClient.invalidateQueries({ queryKey: queryKeys.stats });
    },
  });
}

export function useDeleteDocumentMutation() {
  const queryClient = useQueryClient();
  const setSelectedDocumentIds = useAppStore((state) => state.setSelectedDocumentIds);
  return useMutation({
    mutationFn: (documentId: string) => api.deleteDocument(documentId),
    onSuccess: (_data, documentId) => {
      setSelectedDocumentIds(
        useAppStore.getState().selectedDocumentIds.filter((id) => id !== documentId),
      );
      void queryClient.invalidateQueries({ queryKey: queryKeys.documents });
      void queryClient.invalidateQueries({ queryKey: queryKeys.stats });
    },
  });
}
