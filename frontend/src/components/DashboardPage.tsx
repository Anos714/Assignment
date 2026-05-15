import { FormEvent, useEffect, useMemo, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { ApiError } from "../api/client";
import { ChatPanel } from "./ChatPanel";
import { DocumentsPanel } from "./DocumentsPanel";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import {
  queryKeys,
  useAskQuestionMutation,
  useChat,
  useChats,
  useCreateChatMutation,
  useCurrentUser,
  useDashboardStats,
  useDeleteDocumentMutation,
  useDocuments,
  useUploadDocumentMutation,
} from "../hooks/useApiQueries";
import { useAppStore } from "../store/useAppStore";

const suggestedQuestions = [
  "Summarize the main obligations.",
  "What deadlines or dates are mentioned?",
  "List the risks or termination conditions.",
];

export function DashboardPage() {
  const queryClient = useQueryClient();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [pendingQuestion, setPendingQuestion] = useState("");
  const activeChatId = useAppStore((state) => state.activeChatId);
  const clearSession = useAppStore((state) => state.clearSession);
  const questionDraft = useAppStore((state) => state.questionDraft);
  const selectedDocumentIds = useAppStore((state) => state.selectedDocumentIds);
  const setActiveChatId = useAppStore((state) => state.setActiveChatId);
  const setQuestionDraft = useAppStore((state) => state.setQuestionDraft);
  const setSelectedDocumentIds = useAppStore((state) => state.setSelectedDocumentIds);
  const toggleDocument = useAppStore((state) => state.toggleDocument);

  const meQuery = useCurrentUser();
  const statsQuery = useDashboardStats();
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
    setPendingQuestion(question);
    try {
      await askQuestionMutation.mutateAsync({
        question,
        documentIds: scopedDocumentIds,
      });
      await queryClient.invalidateQueries({ queryKey: queryKeys.chat(activeChatId) });
    } catch {
      setQuestionDraft(question);
    } finally {
      setPendingQuestion("");
    }
  }

  async function handleRefresh() {
    setIsRefreshing(true);
    try {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.me }),
        queryClient.invalidateQueries({ queryKey: queryKeys.stats }),
        queryClient.invalidateQueries({ queryKey: queryKeys.documents }),
        queryClient.invalidateQueries({ queryKey: queryKeys.chats }),
        queryClient.invalidateQueries({ queryKey: queryKeys.ragHealth }),
        activeChatId
          ? queryClient.invalidateQueries({ queryKey: queryKeys.chat(activeChatId) })
          : Promise.resolve(),
      ]);
    } finally {
      setIsRefreshing(false);
    }
  }

  return (
    <main className={isSidebarCollapsed ? "app-shell sidebar-collapsed" : "app-shell"}>
      <Sidebar
        activeChatId={activeChatId}
        chats={chats}
        isCollapsed={isSidebarCollapsed}
        isCreatingChat={createChatMutation.isPending}
        onCreateChat={handleCreateChat}
        onLogout={handleLogout}
        onSelectChat={setActiveChatId}
        onToggleCollapse={() => setIsSidebarCollapsed((isCollapsed) => !isCollapsed)}
        stats={statsQuery.data}
        statsLoading={statsQuery.isLoading}
        user={meQuery.data}
      />

      <section className="workspace" id="workspace">
        <Topbar isRefreshing={isRefreshing} onRefresh={handleRefresh} />

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
            pendingQuestion={pendingQuestion}
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
