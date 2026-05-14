import { create } from "zustand";
import { persist } from "zustand/middleware";

type AppState = {
  accessToken: string | null;
  refreshToken: string | null;
  activeChatId: string | null;
  selectedDocumentIds: string[];
  questionDraft: string;
  setTokens: (tokens: { access: string; refresh: string }) => void;
  clearSession: () => void;
  setActiveChatId: (chatId: string | null) => void;
  toggleDocument: (documentId: string) => void;
  setSelectedDocumentIds: (documentIds: string[]) => void;
  setQuestionDraft: (question: string) => void;
};

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      accessToken: localStorage.getItem("access_token"),
      refreshToken: localStorage.getItem("refresh_token"),
      activeChatId: null,
      selectedDocumentIds: [],
      questionDraft: "",
      setTokens: (tokens) => {
        localStorage.setItem("access_token", tokens.access);
        localStorage.setItem("refresh_token", tokens.refresh);
        set({ accessToken: tokens.access, refreshToken: tokens.refresh });
      },
      clearSession: () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        set({
          accessToken: null,
          refreshToken: null,
          activeChatId: null,
          selectedDocumentIds: [],
          questionDraft: "",
        });
      },
      setActiveChatId: (chatId) => set({ activeChatId: chatId }),
      toggleDocument: (documentId) =>
        set((state) => ({
          selectedDocumentIds: state.selectedDocumentIds.includes(documentId)
            ? state.selectedDocumentIds.filter((id) => id !== documentId)
            : [...state.selectedDocumentIds, documentId],
        })),
      setSelectedDocumentIds: (documentIds) => set({ selectedDocumentIds: documentIds }),
      setQuestionDraft: (question) => set({ questionDraft: question }),
    }),
    {
      name: "knowledge-base-ui",
      partialize: (state) => ({
        activeChatId: state.activeChatId,
        selectedDocumentIds: state.selectedDocumentIds,
      }),
    },
  ),
);
