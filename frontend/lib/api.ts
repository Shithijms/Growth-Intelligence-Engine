// SSE streaming client for the DataVex pipeline API

import { PipelineOutput, ProgressEvent } from './types';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function runPipelineStream(
    keyword: string,
    onProgress: (event: ProgressEvent) => void,
    onResult: (output: PipelineOutput) => void,
    onError: (error: string) => void,
): Promise<void> {
    const response = await fetch(`${BACKEND_URL}/run-pipeline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
        body: JSON.stringify({ keyword }),
    });

    if (!response.ok) {
        onError(`Backend returned ${response.status}`);
        return;
    }

    const reader = response.body?.getReader();
    if (!reader) {
        onError('No response body');
        return;
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        let eventType = '';
        let dataStr = '';

        for (const line of lines) {
            if (line.startsWith('event: ')) {
                eventType = line.slice(7).trim();
            } else if (line.startsWith('data: ')) {
                dataStr = line.slice(6).trim();
            } else if (line === '') {
                // End of SSE message
                if (dataStr) {
                    try {
                        const parsed = JSON.parse(dataStr);
                        if (eventType === 'progress') {
                            onProgress(parsed as ProgressEvent);
                        } else if (eventType === 'result') {
                            onResult(parsed.output as PipelineOutput);
                        } else if (eventType === 'error') {
                            onError(parsed.message || 'Unknown error');
                        }
                    } catch {
                        // Ignore parse errors on individual SSE messages
                    }
                }
                eventType = '';
                dataStr = '';
            }
        }
    }
}

export async function runPipelineSync(keyword: string): Promise<PipelineOutput> {
    const response = await fetch(`${BACKEND_URL}/run-pipeline-sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyword }),
    });
    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || `HTTP ${response.status}`);
    }
    return response.json();
}
