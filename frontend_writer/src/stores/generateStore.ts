import { create } from "zustand";
import { persist } from "zustand/middleware";

export type InputMode = "url" | "content";
export type LengthOption = "short" | "medium" | "long";
export type GenerateView = "input" | "editor";

interface GenerateState {
  sourceUrl: string;
  sourceContent: string;
  topic: string;
  style: string;
  tone: string;
  length: LengthOption;
  output: string;
  outputTitle: string;
  inputMode: InputMode;
  /** 当前视图：input = 输入面板，editor = 富文本编辑器 */
  view: GenerateView;
  /** 用户编辑后的内容（富文本 HTML） */
  editedContent: string;
  /** 用户编辑后的标题 */
  editedTitle: string;
}

interface GenerateActions {
  setSourceUrl: (v: string) => void;
  setSourceContent: (v: string) => void;
  setTopic: (v: string) => void;
  setStyle: (v: string) => void;
  setTone: (v: string) => void;
  setLength: (v: LengthOption) => void;
  setOutput: (v: string) => void;
  setOutputTitle: (v: string) => void;
  setInputMode: (v: InputMode) => void;
  setView: (v: GenerateView) => void;
  setEditedContent: (v: string) => void;
  setEditedTitle: (v: string) => void;
  clearOutput: () => void;
  reset: () => void;
}

const initialState: GenerateState = {
  sourceUrl: "",
  sourceContent: "",
  topic: "",
  style: "technical",
  tone: "professional",
  length: "medium",
  output: "",
  outputTitle: "",
  inputMode: "content",
  view: "input",
  editedContent: "",
  editedTitle: "",
};

export const useGenerateStore = create<GenerateState & GenerateActions>()(
  persist(
    (set) => ({
      ...initialState,

      setSourceUrl: (v) => set({ sourceUrl: v }),
      setSourceContent: (v) => set({ sourceContent: v }),
      setTopic: (v) => set({ topic: v }),
      setStyle: (v) => set({ style: v }),
      setTone: (v) => set({ tone: v }),
      setLength: (v) => set({ length: v }),
      setOutput: (v) => set({ output: v }),
      setOutputTitle: (v) => set({ outputTitle: v }),
      setInputMode: (v) => set({ inputMode: v }),
      setView: (v) => set({ view: v }),
      setEditedContent: (v) => set({ editedContent: v }),
      setEditedTitle: (v) => set({ editedTitle: v }),

      clearOutput: () => set({ output: "", outputTitle: "", editedContent: "", editedTitle: "" }),

      reset: () => set(initialState),
    }),
    {
      name: "ai-writer-generate",
      partialize: (state) => ({
        sourceUrl: state.sourceUrl,
        sourceContent: state.sourceContent,
        topic: state.topic,
        style: state.style,
        tone: state.tone,
        length: state.length,
        output: state.output,
        outputTitle: state.outputTitle,
        inputMode: state.inputMode,
        view: state.view,
        editedContent: state.editedContent,
        editedTitle: state.editedTitle,
      }),
      storage: {
        getItem: (name) => {
          try {
            const value = sessionStorage.getItem(name);
            return value ? JSON.parse(value) : null;
          } catch {
            return null;
          }
        },
        setItem: (name, value) => {
          try {
            sessionStorage.setItem(name, JSON.stringify(value));
          } catch {
            // sessionStorage might be unavailable (private browsing, quota exceeded)
          }
        },
        removeItem: (name) => {
          try {
            sessionStorage.removeItem(name);
          } catch {
            // ignore
          }
        },
      },
    }
  )
);
