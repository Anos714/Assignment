import { FormEvent, useEffect, useMemo } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { ApiError } from "./api/client";
import { AuthPanel } from "./components/AuthPanel";
import { ChatPanel } from "./components/ChatPanel";
import { DocumentsPanel } from "./components/DocumentsPanel";
import { Sidebar } from "./components/Sidebar";
import { Topbar } from "./components/Topbar";
import {
  queryKeys,
  useAskQuestionMutation,
  useChat,
  useChats,
  useCreateChatMutation,
  useCurrentUser,
  useDeleteDocumentMutation,
  useDocuments,
  useUploadDocumentMutation,
} from "./hooks/useApiQueries";
import { useAppStore } from "./store/useAppStore";

const suggestedQuestions = [
  "Summarize the main obligations.",
  "What deadlines or dates are mentioned?",
  "List the risks or termination conditions.",
];

function App() {
  const queryClient = useQueryClient();
  const accessToken = useAppStore((state) => state.accessToken);
  const activeChatId = useAppStore((state) => state.activeChatId);
  const clearSession = useAppStore((state) => state.clearSession);
  const questionDraft = useAppStore((state) => state.questionDraft);
  const selectedDocumentIds = useAppStore((state) => state.selectedDocumentIds);
  const setActiveChatId = useAppStore((state) => state.setActiveChatId);
  const setQuestionDraft = useAppStore((state) => state.setQuestionDraft);
  const setSelectedDocumentIds = useAppStore((state) => state.setSelectedDocumentIds);
  const toggleDocument = useAppStore((state) => state.toggleDocument);

  const meQuery = useCurrentUser();
  const documentsQuery = useDocuments();
  const chatsQuery = useChats();
  const chatQuery = useChat(activeChatId);
  const createChatMutation = useCreateChatMutation();
  const askQuestionMutation = useAskQuestionMutation(activeChatId);
  const uploadDocumentMutation = useUploadDocumentMutation();
  const deleteDocumentMutation = useDeleteDocumentMutation();

  const documents = useMemo(() => documentsQuery.data?.results ?? [], [documentsQuery.data?.results]);
  const chats = useMemo(() => chatsQuery.data?.results ?? [], [chatsQuery.data?.results]);
  const readyDocumentIds = useMemo(
    () => new Set(documents.filter((document) => document.status === "ready").map((document) => document.id)),
    [documents],
  );
  const scopedDocumentIds = selectedDocumentIds.filter((id) => readyDocumentIds.has(id));

  useEffect(() => {
    if (!activeChatId && chats.length > 0) {
      setActiveChatId(chats[0].id);
    }
  }, [activeChatId, chats, setActiveChatId]);

  useEffect(() => {
    if (meQuery.error instanceof ApiError && meQuery.error.status === 401) {
      clearSession();
    }
  }, [clearSession, meQuery.error]);

  useEffect(() => {
    if (documents.length > 0 && selectedDocumentIds.some((id) => !documents.some((document) => document.id === id))) {
      setSelectedDocumentIds(selectedDocumentIds.filter((id) => documents.some((document) => document.id === id)));
    }
  }, [documents, selectedDocumentIds, setSelectedDocumentIds]);

  if (!accessToken) {
    return <AuthPanel />;
  }

  function handleLogout() {
    clearSession();
    queryClient.clear();
  }

  async function handleCreateChat() {
    await createChatMutation.mutateAsync(`Chat ${new Date().toLocaleString()}`);
  }

  async function handleAsk(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const question = questionDraft.trim();
    if (!question || !activeChatId) {
      return;
    }
    setQuestionDraft("");
    try {
      await askQuestionMutation.mutateAsync({
        question,
        documentIds: scopedDocumentIds,
      });
    } catch {
      setQuestionDraft(question);
    }
  }

  function handleRefresh() {
    void queryClient.invalidateQueries({ queryKey: queryKeys.me });
    void queryClient.invalidateQueries({ queryKey: queryKeys.stats });
    void queryClient.invalidateQueries({ queryKey: queryKeys.documents });
    void queryClient.invalidateQueries({ queryKey: queryKeys.chats });
    void queryClient.invalidateQueries({ queryKey: queryKeys.ragHealth });
    if (activeChatId) {
      void queryClient.invalidateQueries({ queryKey: queryKeys.chat(activeChatId) });
    }
  }

  return (
    <main className="app-shell">
      <Sidebar
        activeChatId={activeChatId}
        chats={chats}
        isCreatingChat={createChatMutation.isPending}
        onCreateChat={handleCreateChat}
        onLogout={handleLogout}
        onSelectChat={setActiveChatId}
        user={meQuery.data}
      />

      <section className="workspace" id="workspace">
        <Topbar onRefresh={handleRefresh} />

        {(documentsQuery.error || chatsQuery.error || askQuestionMutation.error || uploadDocumentMutation.error) && (
          <div className="error-banner">
            {formatError(
              documentsQuery.error ??
                chatsQuery.error ??
                askQuestionMutation.error ??
                uploadDocumentMutation.error,
            )}
          </div>
        )}

        <section className="chat-workspace-grid">
          <ChatPanel
            activeChatId={activeChatId}
            isAsking={askQuestionMutation.isPending}
            isLoading={chatQuery.isLoading || chatsQuery.isLoading}
            messages={chatQuery.data?.messages ?? []}
            onAsk={handleAsk}
            onQuestionChange={setQuestionDraft}
            question={questionDraft}
            selectedCount={scopedDocumentIds.length}
            suggestedQuestions={suggestedQuestions}
          />
          <DocumentsPanel
            documents={documents}
            isDeleting={deleteDocumentMutation.isPending}
            isLoading={documentsQuery.isLoading}
            isUploading={uploadDocumentMutation.isPending}
            onDeleteDocument={(documentId) => deleteDocumentMutation.mutate(documentId)}
            onToggleDocument={toggleDocument}
            onUploadDocument={(file) => uploadDocumentMutation.mutate(file)}
            selectedDocumentIds={scopedDocumentIds}
          />
        </section>
      </section>
    </main>
  );
}

function formatError(error: unknown) {
  if (error instanceof ApiError && typeof error.payload === "object" && error.payload) {
    return Object.values(error.payload).flat().join(" ");
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Something went wrong.";
}

export default App;
