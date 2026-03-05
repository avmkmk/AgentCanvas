/**
 * ExecutionWSClient — native browser WebSocket wrapper for execution events.
 *
 * No library required — uses the browser's built-in WebSocket API.
 * Reconnects up to MAX_RECONNECT_ATTEMPTS times with exponential backoff.
 *
 * Coding Standard 2: reconnect timer is always cleared on deliberate disconnect.
 * Coding Standard 8: external WS events are validated before being forwarded.
 */
import type { WSEvent } from "../types";

const WS_BASE =
  (import.meta.env.VITE_WS_BASE_URL as string | undefined) ??
  "ws://localhost:8000";

const MAX_RECONNECT_ATTEMPTS = 3;
const RECONNECT_BASE_DELAY_MS = 2_000;

export class ExecutionWSClient {
  private ws: WebSocket | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private reconnectAttempts = 0;
  private executionId: string | null = null;
  private onEventCallback: ((e: WSEvent) => void) | null = null;
  private onCloseCallback: (() => void) | null = null;

  /** Open a WebSocket connection for the given execution ID. */
  connect(
    executionId: string,
    onEvent: (e: WSEvent) => void,
    onClose: () => void
  ): void {
    this.executionId = executionId;
    this.onEventCallback = onEvent;
    this.onCloseCallback = onClose;
    this.reconnectAttempts = 0;
    this._open();
  }

  private _open(): void {
    if (!this.executionId) return;

    this.ws = new WebSocket(
      `${WS_BASE}/ws/executions/${this.executionId}`
    );

    this.ws.onmessage = (event: MessageEvent) => {
      try {
        const parsed = JSON.parse(event.data as string) as WSEvent;
        // Validate: require the expected shape before forwarding
        if (
          typeof parsed.event === "string" &&
          typeof parsed.execution_id === "string" &&
          typeof parsed.payload === "object" &&
          parsed.payload !== null
        ) {
          this.onEventCallback?.(parsed);
        }
      } catch (err) {
        console.error("[wsClient] Failed to parse WS message:", err);
      }
    };

    this.ws.onclose = () => {
      if (this.reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        this.reconnectAttempts++;
        const delay = RECONNECT_BASE_DELAY_MS * this.reconnectAttempts;
        this.reconnectTimer = setTimeout(() => this._open(), delay);
      } else {
        this.onCloseCallback?.();
      }
    };

    this.ws.onerror = (err) => {
      // onerror is always followed by onclose — reconnect logic is in onclose
      console.error("[wsClient] WebSocket error:", err);
    };
  }

  /** Close the connection and cancel any pending reconnect. */
  disconnect(): void {
    if (this.reconnectTimer !== null) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    // Prevent onclose from triggering another reconnect
    this.reconnectAttempts = MAX_RECONNECT_ATTEMPTS;
    if (this.ws !== null) {
      this.ws.onclose = null;
      this.ws.close();
      this.ws = null;
    }
  }
}
