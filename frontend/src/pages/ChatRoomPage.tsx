import { useEffect, useRef, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Send, Paperclip, ArrowLeft, User } from "lucide-react";
import { chatApi } from "../api";
import { useAuth } from "../context/AuthContext";
import type { ChatMessage, ChatUser } from "../types";

export default function ChatRoomPage() {
  const { userId } = useParams<{ userId: string }>();
  const { user } = useAuth();
  const [roomId, setRoomId] = useState<number | null>(null);
  const [otherUser, setOtherUser] = useState<ChatUser | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [text, setText] = useState("");
  const [attachment, setAttachment] = useState<File | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const lastIdRef = useRef(0);

  useEffect(() => {
    if (!userId) return;
    chatApi.room(Number(userId)).then(({ data }) => {
      setRoomId(data.room_id);
      setOtherUser(data.other_user);
    });
  }, [userId]);

  useEffect(() => {
    if (!roomId) return;
    const poll = () => {
      chatApi.messages(roomId, lastIdRef.current).then(({ data }) => {
        if (data.messages.length > 0) {
          setMessages((prev) => [...prev, ...data.messages]);
          lastIdRef.current = data.messages[data.messages.length - 1].id;
        }
      });
    };
    poll();
    const interval = setInterval(poll, 2000);
    return () => clearInterval(interval);
  }, [roomId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!roomId || (!text.trim() && !attachment)) return;
    await chatApi.send(roomId, text, attachment || undefined);
    setText("");
    setAttachment(null);
    const { data } = await chatApi.messages(roomId, lastIdRef.current);
    if (data.messages.length > 0) {
      setMessages((prev) => [...prev, ...data.messages]);
      lastIdRef.current = data.messages[data.messages.length - 1].id;
    }
  };

  return (
    <div className="mx-auto flex h-[calc(100vh-4rem)] max-w-3xl flex-col px-4 py-4 sm:px-6">
      <div className="card mb-4 flex items-center gap-3 !p-4">
        <Link
          to="/chat"
          className="rounded-lg p-1.5 text-slate-500 hover:bg-slate-100"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        {otherUser?.photo_url ? (
          <img
            src={otherUser.photo_url}
            alt=""
            className="h-10 w-10 rounded-full object-cover"
          />
        ) : (
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
            <User className="h-5 w-5 text-primary" />
          </div>
        )}
        <div>
          <p className="font-semibold text-slate-900">
            {otherUser?.full_name || "Chat"}
          </p>
          <p className="text-xs capitalize text-slate-500">
            {otherUser?.user_type}
          </p>
        </div>
      </div>

      <div className="card flex flex-1 flex-col overflow-hidden !p-0">
        <div className="flex-1 space-y-3 overflow-y-auto p-4">
          {messages.map((m) => {
            const isMine = m.sender_name === user?.username;
            return (
              <div
                key={m.id}
                className={`flex ${isMine ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm ${
                    isMine
                      ? "bg-primary text-white rounded-br-md"
                      : "bg-slate-100 text-slate-800 rounded-bl-md"
                  }`}
                >
                  {!isMine && (
                    <p className="mb-0.5 text-xs font-semibold opacity-70">
                      {m.sender_name}
                    </p>
                  )}
                  <p>{m.message}</p>
                  {m.attachment_url && (
                    <a
                      href={m.attachment_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-1 block text-xs underline"
                    >
                      View attachment
                    </a>
                  )}
                  <p
                    className={`mt-1 text-[10px] ${isMine ? "text-blue-100" : "text-slate-400"}`}
                  >
                    {m.created_at}
                  </p>
                </div>
              </div>
            );
          })}
          <div ref={bottomRef} />
        </div>

        <form
          onSubmit={handleSend}
          className="flex items-center gap-2 border-t border-slate-100 p-3"
        >
          <label className="btn-outline shrink-0 cursor-pointer !px-3 !py-2">
            <Paperclip className="h-4 w-4" />
            <span>{attachment ? "Change file" : "Choose file"}</span>
            <input
              type="file"
              className="hidden"
              onChange={(e) => setAttachment(e.target.files?.[0] || null)}
            />
          </label>

          {attachment && (
            <span className="max-w-32 truncate text-xs text-slate-500">
              {attachment.name}
            </span>
          )}
          <input
            className="input-field flex-1 !py-2"
            placeholder="Type a message..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <button
            type="submit"
            className="rounded-xl bg-primary p-2.5 text-white hover:bg-primary-dark"
          >
            <Send className="h-5 w-5" />
          </button>
        </form>
      </div>
    </div>
  );
}
