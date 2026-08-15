import { describe, expect, it, vi } from "vitest";
import { evaluateProject, type ProjectInput } from "./forgemind-api";

describe("ForgeMind public API client", () => {
  it("sends the public ProjectInput contract to /v1/evaluate", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify({ project: "demo", candidate_count: 0, results: [], engine: "forgemind-python" }), { status: 200, headers: { "content-type": "application/json" } }));
    const project: ProjectInput = { schema_version: "1.0", name: "demo", candidates: [], probes: [], targets: [], metadata: {}, knowledge: [] };
    const response = await evaluateProject(project);
    expect(response.engine).toBe("forgemind-python");
    expect(fetchMock).toHaveBeenCalledWith("/api/engine/v1/evaluate", expect.objectContaining({ method: "POST", body: JSON.stringify({ project }) }));
    vi.restoreAllMocks();
  });
});
