/**
 * useWebSocket — mounts/unmounts the WS connection for an execution.
 *
 * FE-12: called from CanvasPage with the active execution ID so the
 * connection is torn down when navigating away or when the execution ends.
 *
 * Coding Standard 2: always returns a cleanup function that calls disconnectWS.
 */
import { useEffect } from "react";
import { useExecutionStore } from "../store/executionStore";

export function useWebSocket(executionId: string | null): void {
  const connectWS = useExecutionStore((s) => s.connectWS);
  const disconnectWS = useExecutionStore((s) => s.disconnectWS);

  useEffect(() => {
    if (executionId === null) return;

    connectWS(executionId);

    return () => {
      disconnectWS();
    };
    // connectWS/disconnectWS are stable store actions — no re-subscribe needed
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [executionId]);
}
